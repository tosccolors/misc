# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from odoo.addons.account_invoice_import_ml.tests import\
    test_account_invoice_import_ml as ml_test

class TestAccountInvoiceImportMagnus(ml_test.TestAccountInvoiceImportMl):
    def test_email_success(self):
        self._attach(MIMEApplication, 'pdf', 'PDF1', 'invoice1.pdf')
        self._attach(MIMEApplication, 'xml', '<xml/>', 'invoice2.xml')
        self._attach(MIMEApplication, 'vnd.ms-excel', 'XLS1', 'specs.xls')

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(ml_test.SUCCESS_RESULT):
            self.env['mail.thread'].message_process(
                'account.invoice.import', self.mail.as_string(),
            )

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertEqual(len(invoices), 2, 'Only XML and PDF attachments generate an invoice')
        self.assertEqual(invoices.mapped('invoice_line_ids.account_id'), self.account)
        self.assertFalse(invoices.mapped('invoice_line_ids.product_id'))

        attachments = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.invoice'),
            ('res_id', 'in', invoices.ids),
        ])
        self.assertEqual(len(attachments), 6, 'Each attachment is attached to each invoice')

    def test_magnus_address(self):
        mail = MIMEMultipart()
        mail['from'] = 'invoices@magnus.com'
        mail['to'] = 'invoices@yourcompany.com'
        mail.attach(MIMEText('This is your invoice'))
        part = MIMEApplication('PDF1', 'pdf')
        part.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
        mail.attach(part)

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(ml_test.SUCCESS_RESULT):
            self.env['mail.thread'].message_process('account.invoice.import', mail.as_string())

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertNotIn(mail['from'], invoices.partner_id.mapped('child_ids.email'))

    def test_other_address(self):
        mail = MIMEMultipart()
        mail['from'] = 'invoices@othercompany.com'
        mail['to'] = 'invoices@yourcompany.com'
        mail.attach(MIMEText('This is your invoice'))
        part = MIMEApplication('PDF1', 'pdf')
        part.add_header('Content-Disposition', 'attachment', filename='invoice.pdf')
        mail.attach(part)

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(ml_test.SUCCESS_RESULT):
            self.env['mail.thread'].message_process('account.invoice.import', mail.as_string())

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertNotIn(mail['from'], invoices.partner_id.mapped('child_ids.email'))
        self.assertTrue(invoices.source_email)
        invoices.action_create_source_email_partner()
        self.assertIn(mail['from'], invoices.partner_id.mapped('child_ids.email'))
        self.assertFalse(invoices.source_email)

    def test_no_attachment(self):
        mail = MIMEMultipart()
        mail['from'] = 'invoices@magnus.com'
        mail['to'] = 'invoices@yourcompany.com'
        mail.attach(MIMEText('This is your invoice'))

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(ml_test.SUCCESS_RESULT):
            self.env['mail.thread'].message_process('account.invoice.import', mail.as_string())

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertFalse(invoices)
