# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_hide_post_button(self):
        if self.env.user.has_group('bypass_tier_validation.group_bypass_tier_validation'):
            # super hides the button if need_validation is True, we undo this here
            for this in self:
                this._cache['need_validation'] = False
        result = super()._compute_hide_post_button()
        self.invalidate_recordset(['need_validation'], flush=False)
        return result
