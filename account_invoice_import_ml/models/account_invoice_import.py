# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import json
import logging
import requests
from random import random
from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import float_round
from odoo.addons.base.res.res_bank import sanitize_account_number


_logger = logging.getLogger(__name__)


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"

    def fallback_parse_pdf_invoice(self, file_data):
        parsed_data = self._account_invoice_import_ml_parse(file_data)
        if parsed_data.get('failed'):
            return super(AccountInvoiceImport, self).fallback_parse_pdf_invoice(file_data)
        return parsed_data

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        return super(
            AccountInvoiceImport,
            self.with_context(
                account_invoice_import_ml_ignore_failure=True,
                account_invoice_import_ml_vendor_mail=msg_dict.get('email_from'),
            )
        ).message_new(
            msg_dict, custom_values=custom_values
        )

    def _account_invoice_import_ml_parse(self, file_data):
        """Send file to serving container and return its data"""
        response = requests.post(
            self.env['ir.config_parameter'].get_param(
                'account_invoice_import_ml.predict_url'
            ),
            json=self._account_invoice_import_ml_predict_data(
                file_data
            ),
        )
        if response.status_code != 200:
            if self.env.context.get(
                    'account_invoice_import_ml_ignore_failure'
            ):
                _logger.info('Ignoring file data %s...', file_data[:10])
                partner = self.env.ref('account_invoice_import_ml.unknown_supplier')
                return dict(
                    type='in_invoice',
                    partner=dict(recordset=partner),
                    date=False,
                    amount_untaxed=0,
                    amount_tax=0,
                    amount_total=0,
                    invoice_number='Failed',
                )
            else:
                response.raise_for_status()

        response_data = response.json()
        if not response_data.get('vendor_name') and not self.env.context.get(
                'account_invoice_import_ml_ignore_failure'
        ):
            return dict(failed=True)
        return self._account_invoice_import_ml_parse_response(response_data)

    def _account_invoice_import_ml_predict_data(self, file_data):
        """Return data passed to the serving predict endpoint"""
        suppliers = self.env['res.partner'].search([('supplier', '=', True)])
        return {
            "data": base64.b64encode(file_data),
            "vendor_names": suppliers.mapped('name') + suppliers.filtered(
                'supplier_invoice_name'
            ).mapped('supplier_invoice_name'),
        }

    def _account_invoice_import_ml_parse_response(self, response):
        """Return data usable as result of account.invoice.import#parse_pdf_invoice"""
        data = response
        unknown_supplier = self.env.ref('account_invoice_import_ml.unknown_supplier')
        # TODO will the model ever recogize the currency?
        currency = self.env.user.company_id.currency_id
        try:
            partner = self._account_invoice_import_ml_get_vendor(response)
        except UserError:
            if not self.env.context.get(
                    'account_invoice_import_ml_ignore_failure'
            ):
                raise
            partner = unknown_supplier

        from_email = self.env.context.get('account_invoice_import_ml_vendor_mail')
        if partner != unknown_supplier and from_email and partner.email != from_email:
            # add unknown mail address as new partner
            partner = self.env['res.partner'].create({
                'name': partner.name,
                'email': from_email,
                'parent_id': partner.commercial_partner_id.id,
            })
            data.setdefault('__import_ml_warnings', []).append(_(
                'Added unknown email address %s to vendor'
            ) % partner.email)

        if data.get('vendor_bank_account'):
            # warn for unknown account
            sanitized_account = sanitize_account_number(data['vendor_bank_account'])
            existing = self.env['res.partner.bank'].search([
                ('sanitized_acc_number', '=', sanitized_account),
            ])
            if existing and partner != existing.partner_id:
                data.setdefault('__import_ml_warnings', []).append(_(
                    'Supplier coerced from %s to %s by IBAN'
                ) % (partner.name, existing.partner_id.name))
                partner = existing.partner_id
            elif not existing:
                data.setdefault('__import_ml_warnings', []).append(_(
                    'Invoice has unknown IBAN %s'
                ) % sanitized_account)

        self._account_invoice_import_ml_create_partner_config(partner)
        return dict(
            type='in_invoice',
            currency=dict(
                iso=currency.name,
                currency_symbol=currency.symbol,
            ),
            date=data['invoice_date'],
            amount_untaxed=float(data['net_amount']),
            amount_tax=float(data['vat_amount']),
            amount_total=float(data['gross_amount']),
            partner=dict(recordset=partner),
            invoice_number=data['invoice_reference'],
            lines=self._account_invoice_import_ml_parse_response_lines(response),
            import_ml_result=data,
            import_ml_warnings=data.get('__import_ml_warnings') and
            '<ul>' + ''.join(
                '<li>%s</li>' % warning for warning
                in data.get('__import_ml_warnings', [])
            ) + '</ul>' or False
        )

    def _account_invoice_import_ml_get_vendor(self, response):
        """Find a partner based on predictions"""
        partner_dict = {
            'name': response.get('vendor_name'),
        }
        if response.get('vendor_id'):
            partner_dict['ref'] = response['vendor_id'],

        return self.env['business.document.import']._match_partner(
            partner_dict, '',
        )

    def _account_invoice_import_ml_create_partner_config(self, partner):
        config_model = self.env['account.invoice.import.config']
        if not partner:
            return config_model
        config = config_model.search([('partner_id', '=', partner.id)])
        if config:
            return config
        return config_model.create({
            'name': _('Config for %s') % partner.id,
            'partner_id': partner.id,
            'invoice_line_method': '1line_static_product',
            'static_product_id':
            self.env.ref('account_invoice_import_ml.unknown_product').id,
        })

    def _account_invoice_import_ml_parse_response_lines(self, response):
        """Extract invoice lines usable as result of account.invoice.import#parse_pdf_invoice"""
        # TODO at the moment the prediction only has one invoice line
        data = response
        return [
            dict(
                # TODO shouldn't the model also parse unit prices and quantities?
                price_unit=float(data['net_amount']),
                qty=1,
                price_subtotal=float(data['gross_amount']),
                name=data['line_description'],
                # TODO this presupposes that all invoice lines have the same tax and that the tax exists
                taxes=[dict(
                    amount_type='percent',
                    amount=float_round(
                        # TODO as taxes live on invoice lines, we'll need vat/net per line
                        float(data['vat_amount']) / (float(data['net_amount']) or 1),
                        precision_digits=self.env['decimal.precision'].precision_get('Account'),
                    ) * 100,
                )],
                # TODO this needs a patch in account_invoice_import to have _prepare_create_invoice_vals pick up those values
                account=dict(
                    code=data['account_number'],
                    name=data['account_name'],
                ),
                analytic_account=dict(
                    code=data['analytic_account_code'],
                    name=data['analytic_account_name'],
                ),
                operating_unit=dict(
                    # TODO wouldn't an id or code be more in line with the above?
                    name=data['operating_unit'],
                ),
            ),
        ]

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config=False):
        vals, config = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(
            parsed_inv, import_config=import_config,
        )
        if 'import_ml_result' in parsed_inv:
            field_mappings = {
                'vendor_name': 'partner_id',
                'invoice_date': 'date_invoice',
                'net_amount': 'amount_untaxed',
                'vat_amount': 'amount_tax',
                'gross_amount': 'amount_total',
                'invoice_reference': 'invoice_number',
            }
            for key, value in field_mappings.items():
                field_mappings['%s_confidence' % key] = '%s_confidence' % (
                    value
                )
            vals['import_ml_result'] = {
                field_mappings.get(key, key): value
                for key, value in parsed_inv['import_ml_result'].items()
            }
            # TODO remove this when the container returns confidences
            for key, value in vals['import_ml_result'].items():
                if not key.endswith('_confidence') and '%s_confidence' % key not in vals['import_ml_result']:
                    vals['import_ml_result']['%s_confidence' % key] = random()
        if 'import_ml_warnings' in parsed_inv:
            vals['import_ml_warnings'] = parsed_inv['import_ml_warnings']
        return vals, config
