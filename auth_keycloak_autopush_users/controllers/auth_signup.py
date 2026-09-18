from odoo import http
from odoo.addons.auth_signup.controllers import main as auth_signup_main


class AuthSignupHome(auth_signup_main.AuthSignupHome):
    def _signup_with_values(self, token, values):
        result = super()._signup_with_values(token, values)

        cr = http.request.env.cr

        def reset_signup_password(cr=cr, login=values.get('login')):
            cr.execute("UPDATE res_users SET password=NULL WHERE login=%s", (login,))

        # do_signup commits after calling _signup_with_values,
        # at that point we cannot commit yet because web_auth_signup
        # calls login web_login at which point the password must exist
        http.request.env.cr.postcommit.add(
            lambda cr=cr: cr.precommit.add(reset_signup_password)
        )

        return result
