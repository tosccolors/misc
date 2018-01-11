# -*- coding: utf-8 -*-
from odoo import tools, api, fields, models, _

class Partner(models.Model):
    _inherit = ['res.partner']

    transmit_invoice = fields.Selection([('email','Email'),('other','Other')], string = 'Transmit Invoice')

Partner()