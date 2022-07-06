# -*- coding: utf-8 -*-


import logging


from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    # Overridden:
    @api.multi
    def action_reset_password(self):
        return True
