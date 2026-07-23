from odoo import api, fields, models, exceptions

class PortalWizardUser(models.TransientModel):

    _inherit = 'portal.wizard.user'

    def action_grant_access(self):
        result = super().action_grant_access()
        push_wizard = self._get_push_wizard()
        if push_wizard:
            push_wizard.button_create_user()
        return result

    def _send_email(self):
        push_wizard = self._get_push_wizard()
        if push_wizard and push_wizard.provider_id.disable_welcome_email:
            return True
        return super()._send_email()

    def action_invite_again(self):
        push_wizard = self._get_push_wizard()
        if push_wizard and push_wizard.provider_id.disable_welcome_email:
            return self.partner_id.user_ids[:1].action_reset_password()
        return super().action_invite_again()


    def _get_push_wizard(self):
        user = self.partner_id.user_ids[:1]
        if user:
            push_action = user.button_push_to_keycloak()
            return self.env[push_action['res_model']].browse(push_action['res_id'])
        return False
