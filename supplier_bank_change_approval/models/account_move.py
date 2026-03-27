from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    # Update vendor bank account in account invoice on_change checking
    
    _inherit = 'account.move'
        
    @api.constrains('partner_id')
    def _check_partner_id(self):
        bank_list=[]
        for this in self:
            if this.move_type != 'in_invoice':
                continue

            if not any(state == 'confirmed' for state in this.partner_id.bank_ids.mapped('state')):
                raise UserError(_('The supplier has changed bank details which are not yet approved.'))
