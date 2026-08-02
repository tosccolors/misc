import requests
from odoo import api, fields, models, exceptions
from odoo.addons.auth_keycloak.wizard.auth_keycloak_sync_mixin import KEYCLOAK_TIMEOUT

class AuthKeycloakCreateWiz(models.TransientModel):
    _inherit = 'auth.keycloak.create.wiz'

    def _send_update_password_mail(self, token, odoo_user, keycloak_user):
        if self.env.context.get("auth_keycloak_autopush_users_inhbit_password_mail"):
            return
        return super()._send_update_password_mail(token, odoo_user, keycloak_user)

    def _set_keycloak_password(self, user, password):
        url = f"{self.endpoint}/{user.oauth_uid}/reset-password"
        token = self._get_token()
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        response = requests.put(
            url, headers=headers, json={
                "type": "password",
                "value": password,
                "temporary": False
            },
            timeout=KEYCLOAK_TIMEOUT
        )
        self._validate_response(response, no_json=True)

    def _send_otp_mail(self, user):
        token = self._get_token()
        url = f"{self.endpoint}/{user.oauth_uid}/execute-actions-email"
        headers = {
            "Authorization": "Bearer %s" % token,
        }
        resp = requests.put(
            url, headers=headers, json=["CONFIGURE_TOTP"], timeout=KEYCLOAK_TIMEOUT
        )
        self._validate_response(resp, no_json=True)
