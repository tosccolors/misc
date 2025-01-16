# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = "account.payment.line.create"

    def _prepare_move_line_domain(self):
        operating_unit_id = self.order_id.operating_unit_id.id
        result = super()._prepare_move_line_domain()
        return result + (
            [
                '|', ('operating_unit_id', '=', operating_unit_id),
                ('operating_unit_id', '=', False),
            ]
            if self.order_id.operating_unit_id else []
        )
