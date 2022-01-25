# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    ml_min_confidence_partner = fields.Float(
        'Minimal confidence for partners', default=.5,
    )
    ml_fallback_partner_id = fields.Many2one('res.partner')
    ml_min_confidence_account = fields.Float(
        'Minimal confidence for accounts', default=.75,
    )
    ml_fallback_account_id = fields.Many2one('account.account')
