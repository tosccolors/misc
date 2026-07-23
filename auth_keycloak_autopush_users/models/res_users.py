import requests
from odoo import fields, models, api
from odoo.addons.auth_keycloak.wizard.auth_keycloak_sync_mixin import KEYCLOAK_TIMEOUT


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        keycloak_users = self.filtered(lambda x: x.oauth_provider_id)
        for keycloak_user in keycloak_users:
            provider = keycloak_user.oauth_provider_id
            wizard = self.env["auth.keycloak.create.wiz"].new({
                "provider_id": provider.id,
                "management_enabled": provider.users_management_enabled,
                "endpoint": provider.users_endpoint,
                "user": provider.superuser,
                "pwd": provider.superuser_pwd,
            })
            token = wizard._get_token()
            wizard._send_update_password_mail(token, keycloak_user, {'id': keycloak_user.oauth_uid})
        self = self - keycloak_users
        return super().action_reset_password()

    @api.model
    def _signup_create_user(self, values):
        user = super()._signup_create_user(values)
        push_wizard = self.env["portal.wizard.user"].new({
            "partner_id": user.partner_id,
        })._get_push_wizard()
        if push_wizard:
            push_wizard.with_context(auth_keycloak_autopush_users_inhbit_password_mail=True).button_create_user()
            url = f"{push_wizard.endpoint}/{user.oauth_uid}/reset-password"
            token = push_wizard._get_token()
            headers = {
                "Authorization": "Bearer %s" % token,
            }
            response = requests.put(
                url, headers=headers, json={
                    "type": "password",
                    "value": values.get("password"),
                    "temporary": False
                },
                timeout=KEYCLOAK_TIMEOUT
            )
            push_wizard._validate_response(response, no_json=True)
        return user
