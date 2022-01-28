# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_invoice_name = fields.Char(
        help='If the name on an invoice from this supplier differs from the '
        'name in Odoo, fill in the name on the invoice here'
    )
