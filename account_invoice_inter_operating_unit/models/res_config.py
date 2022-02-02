# -*- coding: utf-8 -*-
from odoo import models, fields


class InterCompanyRulesAccountConfig(models.TransientModel):

    _inherit = 'res.config.settings'

    invoice_auto_validation = fields.Boolean(
        related='operating_unit_id.invoice_auto_validation',
        string='Invoices Auto Validation',
        help='When an invoice is created by a multi OU/company rule for '
             'this operating unit, it will automatically validate it.')
