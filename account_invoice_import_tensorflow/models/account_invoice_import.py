# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import requests
from odoo import models
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
        #response = requests.post(
        #    self.env['ir.config_parameter'].get_param(
        #        'account_invoice_import_tensorflow.predict_url'
        #    ),
        #    json=self._account_invoice_import_tensorflow_predict_data(
        #        file_data
        #    ),
        #)
        # return self._account_invoice_import_tensorflow_parse_response(response.json())
        response_data = dict(predictions=json.loads(file_data))
        if not response_data['predictions']:
            # TODO how does a response of a failed prediction look?
            return dict(failed=True)
        return self._account_invoice_import_tensorflow_parse_response(response_data)

    def _account_invoice_import_tensorflow_predict_data(self, file_data):
        """Return data passed to the serving predict endpoint"""
        # TODO how do we need to format our input?
        return {
            "inputs": base64.b64encode(file_data),
        }

    def _account_invoice_import_tensorflow_parse_response(self, response):
        """Return data usable as result of account.invoice.import#parse_pdf_invoice"""
        data = response['predictions']
        # TODO will the model ever recogize the currency?
        currency = self.env.user.company_id.currency_id
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
            partner=dict(recordset=self.env['res.partner'].browse(int(data['vendor_id']))),
            invoice_number=data['invoice_reference'],
            lines=self._account_invoice_import_tensorflow_parse_response_lines(response),
        )

    def _account_invoice_import_tensorflow_parse_response_lines(self, response):
        """Extract invoice lines usable as result of account.invoice.import#parse_pdf_invoice"""
        # TODO at the moment the json file only has one invoice line
        data = response['predictions']
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
                        float(data['vat_amount']) / float(data['net_amount']),
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
