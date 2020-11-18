# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import json
import requests
from odoo import _, models
from odoo.tools import float_round


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"

    def fallback_parse_pdf_invoice(self, file_data):
        parsed_data = self._account_invoice_import_tensorflow_parse(file_data)
        if parsed_data.get('failed'):
            return super(AccountInvoiceImport, self).fallback_parse_pdf_invoice(file_data)
        return parsed_data

    def _account_invoice_import_tensorflow_parse(self, file_data):
        """Send file to serving container and return its data"""
        response_data = requests.post(
            self.env['ir.config_parameter'].get_param(
                'account_invoice_import_tensorflow.predict_url'
            ),
            json=self._account_invoice_import_tensorflow_predict_data(
                file_data
            ),
        ).json()
        if not response_data.get('vendor_name'):
            return dict(failed=True)
        return self._account_invoice_import_tensorflow_parse_response(response_data)

    def _account_invoice_import_tensorflow_predict_data(self, file_data):
        """Return data passed to the serving predict endpoint"""
        return {
            "data": base64.b64encode(file_data),
        }

    def _account_invoice_import_tensorflow_parse_response(self, response):
        """Return data usable as result of account.invoice.import#parse_pdf_invoice"""
        data = response
        # TODO will the model ever recogize the currency?
        currency = self.env.user.company_id.currency_id
        partner = self._account_invoice_import_tensorflow_get_vendor(response)
        self._account_invoice_import_tensorflow_create_partner_config(partner)
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
            partner=dict(recordset=partner) if partner else dict(
                name=response['vendor_name'],
            ),
            invoice_number=data['invoice_reference'],
            lines=self._account_invoice_import_tensorflow_parse_response_lines(response),
        )

    def _account_invoice_import_tensorflow_get_vendor(self, response):
        """Find a partner based on predictions"""
        return self.env['res.partner'].search(
            [
                '|',
                ('name', '=', response.get('vendor_name')),
                ('ref', '=', response.get('vendor_id')),
            ], limit=1,
        )

    def _account_invoice_import_tensorflow_create_partner_config(self, partner):
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
            self.env.ref('account_invoice_import_tensorflow.unknown_product').id,
        })

    def _account_invoice_import_tensorflow_parse_response_lines(self, response):
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
