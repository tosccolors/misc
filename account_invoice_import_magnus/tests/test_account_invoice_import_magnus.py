# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from odoo.addons.account_invoice_import_ml.tests import\
    test_account_invoice_import_ml as ml_test

class TestAccountInvoiceImportMagnus(ml_test.TestAccountInvoiceImportMl):
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

    def test_no_attachment(self):
        mail = MIMEMultipart()
        mail['from'] = 'invoices@magnus.com'
        mail['to'] = 'invoices@yourcompany.com'
        mail.attach(MIMEText('This is your invoice'))

        existing_invoices = self.env['account.invoice'].search([])

        with self._mock(ml_test.SUCCESS_RESULT):
            self.env['mail.thread'].message_process('account.invoice.import', mail.as_string())

        invoices = self.env['account.invoice'].search([]) - existing_invoices
        self.assertTrue(invoices)
