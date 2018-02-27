# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one('operating.unit', related='account_id.operating_unit_id', string="Operating Unit", store=True)