from odoo import api, fields, models, _
from datetime import datetime, date

class MontaConfig(models.Model):
    _name = "monta.config"
    _description = 'Monta Config'
    _rec_name = 'username'

    host = fields.Char('URL', required=True,
        help='This is the URL that the system can be reached at.'
    )
    username = fields.Char('Username', required=True,
        help='This is the username that is used for authenticating to this '
             'system, if applicable.',
    )
    password = fields.Char('Password', required=True,
        help='This is the password that is used for authenticating to this '
             'system, if applicable.',
    )
    origin = fields.Char('Origin', required=True,
                       help='This is the URL that the system can be reached at.'
                       )