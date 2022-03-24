# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    trading_partner_code = fields.Char('Trading Partner Code', help="Specify code of Trading Partner")