# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountPaymentLine(models.Model):
    _inherit = 'account.payment.line'


    def _prepare_account_payment_vals(self):
        result = super()._prepare_account_payment_vals()
        result['operating_unit_id'] = self.order_id.operating_unit_id.id
        return result
