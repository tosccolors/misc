# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _prepare_entry_lines(self, new_move, period, amount, is_cutoff=True):
        self = self.with_context(default_operating_unit_id=self.operating_unit_id.id)
        return super()._prepare_entry_lines(new_move, period, amount, is_cutoff=is_cutoff)
