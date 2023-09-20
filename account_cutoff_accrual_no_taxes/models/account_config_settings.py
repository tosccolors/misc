# -*- coding: utf-8 -*-

from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    accrual_no_taxes = fields.Boolean(
        related='company_id.accrual_no_taxes')
