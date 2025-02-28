from odoo.tests.common import TransactionCase


mail = """From: test@test.com
Subject: Your invoice"""


class TestAccountInvoiceImportOperatingUnit(TransactionCase):
    def test_mail_fetching(self):
        server = self.env['fetchmail.server'].create({
            'name': 'OU server',
            'server_type': 'local',
            'operating_unit_id': self.env.ref('operating_unit.b2c_operating_unit').id,
        })
        self.env['mail.thread'].with_context(
            default_fetchmail_server_id=server.id,
        ).message_process('account.invoice.import', mail)

