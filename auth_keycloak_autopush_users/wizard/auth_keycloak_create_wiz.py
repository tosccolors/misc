from odoo import api, fields, models, exceptions

class AuthKeycloakCreateWiz(models.TransientModel):
    _inherit = 'auth.keycloak.create.wiz'

    def _send_update_password_mail(self, token, odoo_user, keycloak_user):
        if self.env.context.get("auth_keycloak_autopush_users_inhbit_password_mail"):
            return
        return super()._send_update_password_mail(token, odoo_user, keycloak_user)
