# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Lead(models.Model):
    _inherit = "crm.lead"

    is_partner_log = fields.Boolean('Is Partner Log?')

