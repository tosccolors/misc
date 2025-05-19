from odoo import fields, models


class AccountAccountType(models.Model):
    _inherit = "account.account.type"

    property_default_account = fields.Many2one('account.analytic.account', string='Default account', company_dependent=True)
