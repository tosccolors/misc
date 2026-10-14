from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    session_keepalive_timeout = fields.Float(help='Keepalive timeout in hours', config_parameter='session_keepalive.timeout')
