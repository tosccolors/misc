from odoo import models, fields, api, _
from odoo.exceptions import UserError

   
class AccountPayment(models.Model):
    
    # Update  vendor bank account in account payment checking
    
    _inherit = 'account.payment'

    @api.constrains('partner_id')
    def _check_partner_id(self):
        bank_payment_list=[]
        for this in self:
            if this.partner_id.supplier_rank:
                if not any(state == 'confirmed' for state in this.partner_id.bank_ids.mapped('state')):
                    raise UserError(_('The supplier has changed bank details which are not yet approved.'))
