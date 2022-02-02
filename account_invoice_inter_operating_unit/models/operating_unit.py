# -*- coding: utf-8 -*-
from odoo import api, fields, models



class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    invoice_auto_validation = fields.Boolean(
        string='Invoice Auto Validation',
        help="When an invoice is created by a multi company rule "
             "for this operating unit, it will automatically validate it",
        default=True)

    @api.model
    def _find_operating_unit_from_partner(self, partner_id):
        operating_unit = self.sudo().search([('partner_id', '=', partner_id)],
                                     limit=1)
        return operating_unit or False
