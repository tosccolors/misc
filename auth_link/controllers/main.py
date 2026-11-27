import werkzeug
import json
from odoo import _, exceptions, fields, http


class AuthLinkController(http.Controller):
    @http.route("/auth_link/<key>", auth='public')
    def auth_link(self, key):
        result = self._authenticate(key)
        return http.request.redirect(result['redirect'])

    @http.route("/auth_link/<key>/json", auth='public')
    def auth_link_json(self, key):
        return json.dumps(self._authenticate(key, raise_on_failure=False))

    @http.route("/auth_link/<key>/check", auth='public')
    def auth_link_check(self, key):
        return json.dumps(self._authenticate(key, raise_on_failure=False, update_session=False))

    def _authenticate(self, key, raise_on_failure=True, update_session=True):
        env = http.request.env
        if not env.user._is_public():
            if raise_on_failure:
                raise exceptions.UserError(_('You are already logged in'))
            else:
                return {"status": "failure"}
        Apikeys = env['auth_link.apikeys'].sudo()
        user_id = Apikeys._check_credentials(scope='auth_link', key=key)
        if not user_id:
            if raise_on_failure:
                raise werkzeug.exceptions.Unauthorized()
            else:
                return {"status": "failure"}

        key_record = Apikeys._get_key_record(key)

        if not key_record or (key_record.expires and fields.Datetime.now() > key_record.expires):
            if raise_on_failure:
                raise werkzeug.exceptions.Unauthorized()
            else:
                return {"status": "failure"}

        user = env['res.users'].sudo().browse(user_id).with_user(user_id)

        result = {
            "status": "ok",
            "expires": key_record.expires and key_record.expires.timestamp() or 0,
            "expires_in": key_record.expires and (key_record.expires - fields.Datetime.now()).total_seconds() or 0,
            "redirect": key_record.redirect or (key_record.user_id.has_group('base.group_user') and '/web' or '/my'),
            "key": key,
        }

        if update_session:
            http.request.session.update({
                'db': env.registry.db_name,
                'login': user.login,
                'uid': user.id,
                'context': dict(user.context_get()),
                'session_token': user._compute_session_token(http.request.session.sid),
            })
            result["session_id"] = http.request.session.sid
        http.request._save_session()

        return result
