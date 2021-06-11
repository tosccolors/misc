# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    invoice_import_email = fields.Char()
