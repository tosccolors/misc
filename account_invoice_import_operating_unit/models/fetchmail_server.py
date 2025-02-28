# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class FetchmailServer(models.Model):
    _inherit = "fetchmail.server"

    operating_unit_id = fields.Many2one('operating.unit')
