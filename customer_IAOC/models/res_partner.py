# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields,_
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    vat = fields.Char("TIN")