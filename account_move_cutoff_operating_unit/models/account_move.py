# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _prepare_deferred_entry(self, journal, date_, reference):
        result = super()._prepare_deferred_entry(journal, date_, reference)
        return dict(result, operating_unit_id=self.operating_unit_id.id)
