from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountPaymentOrder(models.Model):

    # checking bank account of Partner in account payment order

    _inherit = 'account.payment.order'

    def draft2open(self):
        for partner in self.payment_line_ids.partner_id:
            if not any(state == 'confirmed' for state in partner.bank_ids.mapped('state')):
                raise UserError(_('The supplier {0} has changed bank details which are not yet approved.'.format(partner.name)))
        return super().draft2open()
