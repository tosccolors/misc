# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import mock
from contextlib import contextmanager
from odoo.tests.common import  TransactionCase


SUCCESS_RESULT = {
    'vendor_name': 'Camptocamp',
    'invoice_date': '2020-01-01',
    'net_amount': 42.42,
    'gross_amount': 42.42,
    'vat_amount': 0,
    'invoice_reference': 'REF',
    'line_description': 'desc',
    'account_number': '4242',
    'account_name': '4242',
    'analytic_account_code': '43',
    'analytic_account_name': '43',
    'operating_unit': '44',
    # randomly generated
    'vendor_bank_account': 'NL47INGB4395098177',
}


class TestAccountInvoiceImportMl(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceImportMl, self).setUp()
        # delete existing demo data draft invoices because they interfere with tests
        self.env['account.invoice'].search([
            ('partner_id', '=', self.env.ref('base.res_partner_12').id),
            ('state', '=', 'draft'),
        ]).unlink()

    def test_wrong_iban(self):
        # test we find suppliers by name if the iban isn't known
        with self._mock(SUCCESS_RESULT):
            invoices = self.env['account.invoice'].search([])
            self._import_file()
            new_invoice = self.env['account.invoice'].search([]) - invoices
            # res_partner_12 is camptocamp
            self.assertEqual(new_invoice.partner_id, self.env.ref('base.res_partner_12'))
        new_partner = self.env['res.partner'].create({
            'name': 'new',
        })
        new_iban = self.env['res.partner.bank'].create({
            'partner_id': new_partner.id,
            'acc_number': SUCCESS_RESULT['vendor_bank_account'],
        })
        # test we find suppliers by deviating iban
        with self._mock(SUCCESS_RESULT):
            invoices = self.env['account.invoice'].search([])
            self._import_file()
            new_invoice = self.env['account.invoice'].search([]) - invoices
            self.assertEqual(new_invoice.partner_id, new_partner)
            self.assertIn('coerced', new_invoice.import_ml_warnings)
        pass

    @contextmanager
    def _mock(self, payload):
        with mock.patch(
                'odoo.addons.account_invoice_import_ml.models.'
                'account_invoice_import.requests.post'
        ) as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = payload
            yield mock_post

    def _import_file(self):
        self.env['account.invoice.import'].create({
            'invoice_file': base64.b64encode('hello world'),
            'invoice_filename': 'hello.pdf',
        }).import_invoice()
