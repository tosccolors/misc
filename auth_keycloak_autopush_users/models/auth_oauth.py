
from odoo import fields, models, api


class OAuthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    disable_welcome_email = fields.Boolean("Disable sending Welcome Mail from Odoo?", default=True)

