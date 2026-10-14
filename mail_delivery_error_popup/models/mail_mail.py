from odoo import _, api, fields, models


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _postprocess_sent_message(self, success_pids, failure_reason=False, failure_type=None):
        if failure_reason or failure_type:
            self._mail_delivery_error_popup()
        return super()._postprocess_sent_message(success_pids, failure_reason=failure_reason, failure_type=failure_type)

    def _mail_delivery_error_popup(self):
        notify_group = self.env.ref('mail_delivery_error_popup.group_mail_delivery_error_popup')
        for this in self:
            Model = self.env.get(this.model)
            record = Model is not None and Model.browse(this.res_id or []) or this
            notify_users = notify_group.users | record.create_uid
            for user in notify_users:
                user.sudo().notify_danger(
                    title=_('Mail delivery failed: %s') % record.display_name,
                    message=this.failure_reason,
                    action={
                        'type': 'ir.actions.act_window',
                        'res_model': record._name,
                        'res_id': record.id,
                        'views': [(False, 'form')],
                    },
                    sticky=True,
                )
