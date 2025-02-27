# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AgedPartnerBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.aged_partner_balance"

    @api.model
    def _get_new_move_lines_domain(
        self, new_ml_ids, account_ids, company_id, partner_ids, only_posted_moves
    ):
        result = super()._get_new_move_lines_domain(new_ml_ids, account_ids, company_id, partner_ids, only_posted_moves)
        operating_unit_ids = self.env.context.get("operating_unit_ids", [])
        if operating_unit_ids:
            result.extend(['|', ("operating_unit_id", "in", operating_unit_ids), ("operating_unit_id", "=", False)])
        return result
