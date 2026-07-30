from odoo import fields, models, api
from odoo.exceptions import AccessDenied


class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        keycloak_users = self.filtered("oauth_provider_id.users_management_enabled")
        for keycloak_user in keycloak_users:
            wizard = keycloak_user._get_push_wizard()
            token = wizard._get_token()
            wizard._send_update_password_mail(token, keycloak_user, {'id': keycloak_user.oauth_uid})
        self = self - keycloak_users
        return super().action_reset_password()

    def _set_password(self):
        keycloak_users = self.filtered("oauth_provider_id.users_management_enabled")
        for keycloak_user in keycloak_users:
            wizard = keycloak_user._get_push_wizard()
            wizard._set_keycloak_password(keycloak_user, keycloak_user.password)
        self = self - keycloak_users
        return super()._set_password()

    def action_send_keycloak_otp_mail(self):
        keycloak_users = self.filtered("oauth_provider_id.users_management_enabled")
        for keycloak_user in keycloak_users:
            wizard = keycloak_user._get_push_wizard()
            wizard._send_otp_mail(keycloak_user)

    @api.model
    def change_password(self, old_passwd, new_passwd):
        if self.env.user.filtered("oauth_provider_id.users_management_enabled"):
            keycloak_user = self.env.user
            wizard = keycloak_user._get_push_wizard(user=keycloak_user.login, pwd=old_passwd)
            try:
                # verify old password is correct
                wizard._get_token()
            except Exception as e:
                raise AccessDenied() from e
            wizard = keycloak_user._get_push_wizard()
            wizard._set_keycloak_password(keycloak_user, new_passwd)
        else:
            return super().change_password()

    @api.model
    def _signup_create_user(self, values):
        user = super()._signup_create_user(values)
        push_wizard = self.env["portal.wizard.user"].new({
            "partner_id": user.partner_id,
        })._get_push_wizard()
        if push_wizard:
            push_wizard.with_context(auth_keycloak_autopush_users_inhbit_password_mail=True).button_create_user()
            push_wizard._set_keycloak_password(user, values.get("password"))
        return user

    def _get_push_wizard(self, **extra_wizard_vals):
        provider = self.oauth_provider_id
        wizard = self.env["auth.keycloak.create.wiz"].new({
            "provider_id": provider.id,
            "management_enabled": provider.users_management_enabled,
            "endpoint": provider.users_endpoint,
            "user": provider.superuser,
            "pwd": provider.superuser_pwd,
            **extra_wizard_vals,
        })
        return wizard

    def _get_my_security_link(self):
        provider = self.sudo().oauth_provider_id
        if provider.auth_endpoint:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            account_url = provider.auth_endpoint.replace('protocol/openid-connect/auth', 'account')
            account_url += f'?referrer={provider.client_id}&referrer_uri={base_url}/my'
            return account_url
        return "/my/security"
