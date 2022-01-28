# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import mock
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        self.account = self.env['account.account'].create({
            'name': SUCCESS_RESULT['account_name'],
            'code': SUCCESS_RESULT['account_number'],
            'user_type_id': self.env.ref('account.data_account_type_payable').id,
            'reconcile': True,
        })
        self.mail = MIMEMultipart()
        self.mail['from'] = 'invoices@test-supplier.com'
        self.mail['to'] = 'invoices@yourcompany.com'
        self.mail.attach(MIMEText('This is your invoice'))


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

    def test_email_success(self):
        self._attach(MIMEApplication, 'pdf', 'PDF1', 'invoice1.pdf')
        self._attach(MIMEApplication, 'vnd.ms-excel', 'XLS1', 'specs.xls')

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(SUCCESS_RESULT):
            self.env['mail.thread'].message_process(
                'account.invoice.import', self.mail.as_string(),
            )

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        # given the way we mock the container above, all files will come back as valid
        # the real container will error out on the xls file
        self.assertEqual(len(invoices), 2, 'Each attachment generates an invoice')
        self.assertEqual(invoices.mapped('invoice_line_ids.account_id'), self.account)
        self.assertFalse(invoices.mapped('invoice_line_ids.product_id'))

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.invoice'),
            ('res_id', 'in', invoices.ids),
        ])
        self.assertEqual(len(attachments), 4, 'Each attachment is attached to each invoice')

    def test_email_failure(self):
        self._attach(MIMEApplication, 'pdf', 'PDF1', 'invoice1.pdf')

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(dict(SUCCESS_RESULT, vendor_name=''), 400):
            self.env['mail.thread'].message_process(
                'account.invoice.import', self.mail.as_string(),
            )

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertEqual(
            invoices.partner_id,
            self.env.ref('account_invoice_import_ml.unknown_supplier'),
        )

    @contextmanager
    def _mock(self, payload, status_code=200):
        with mock.patch(
                'odoo.addons.account_invoice_import_ml.models.'
                'account_invoice_import.requests.post'
        ) as mock_post:
            mock_post.return_value.status_code = status_code
            mock_post.return_value.json.return_value = payload
            yield mock_post

    def _attach(self, cls, subtype, data, filename):
        part = cls(data, subtype)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        self.mail.attach(part)

    def _import_file(self):
        self.env['account.invoice.import'].create({
            'invoice_file': base64.b64encode('hello world'),
            'invoice_filename': 'hello.pdf',
        }).import_invoice()
