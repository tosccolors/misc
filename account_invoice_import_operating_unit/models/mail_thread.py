# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):
        mail_server_id = self.env.context.get(
            'default_fetchmail_server_id'
        )
        mail_server = self.env['fetchmail.server'].browse(mail_server_id or [])
        if mail_server.operating_unit_id:
            self = self.with_context(default_operating_unit_id=mail_server.operating_unit_id.id)
        return super().message_process(
            model, message, custom_values=custom_values,
            save_original=save_original, strip_attachments=strip_attachments,
            thread_id=thread_id
        )
