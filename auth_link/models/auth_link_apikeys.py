from odoo import api, fields, models
from odoo.addons.base.models.res_users import KEY_CRYPT_CONTEXT, INDEX_SIZE
from urllib.parse import urlsplit, urlunsplit


class AuthLinkApikeys(models.Model):
    _name = 'auth_link.apikeys'
    _inherit = 'res.users.apikeys'
    _description = 'Keys for authentication links'
    _log_access = False

    id = fields.Id()
    expires = fields.Datetime(required=True)
    redirect = fields.Char()

    def init(self):
        super().init()
        self.env.cr.execute(
            f"""
            ALTER TABLE {self._table}
            ADD COLUMN IF NOT EXISTS expires timestamp without time zone,
            ADD COLUMN IF NOT EXISTS redirect varchar
            """,
        )

    def _generate_link_for_user(self, user, expires=None, redirect=None):
        key = self.with_user(user)._generate(scope="auth_link", name="Auth link")
        key_record = self.sudo()._get_key_record(key)
        key_record.write({
            'expires': expires,
            'redirect': redirect,
        })
        url = urlsplit(user.get_base_url())
        return urlunsplit(url._replace(path="/auth_link/" + key))

    def _get_key_record(self, key):
        self.env.cr.execute(f"SELECT id, key FROM {self._table} WHERE index=%s", (key[:INDEX_SIZE],))
        for _id, _key in self.env.cr.fetchall():
            if KEY_CRYPT_CONTEXT.verify(key, _key):
                return self.browse(_id)
        return self.browse([])

    @api.autovacuum
    def _gc_link_api_keys(self):
        self.env.cr.execute(f"DELETE FROM {self._table} WHERE expires < NOW()")
