# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    trade_partner_code = fields.Char('Trade Partner Code', help="Specify code of Trade Partner")