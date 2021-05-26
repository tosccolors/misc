# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = "account.config.settings"

    ml_min_confidence_partner = fields.Float(related='company_id.ml_min_confidence_partner')
    ml_fallback_partner_id = fields.Many2one(related='company_id.ml_fallback_partner_id')
    ml_min_confidence_account = fields.Float(related='company_id.ml_min_confidence_account')
    ml_fallback_account_id = fields.Many2one(related='company_id.ml_fallback_account_id')
