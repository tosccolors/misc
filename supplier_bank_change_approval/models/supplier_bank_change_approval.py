# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SupplierBankApproval(models.Model):
   
       #Update vendor bank account with states 
    
    _inherit = 'res.partner.bank'
    
    state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed")],default='draft',string='Status', copy=False, index=True,readonly=True, store=True,track_visibility='always')
    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
       
    @api.multi
    def write(self, vals):
        # Update vendor bank account then  
        # :return:state Draft
        
        if self.partner_id.supplier==True:
            if self.state=='confirmed':
                vals.update({'state' : 'draft'})
        return super(SupplierBankApproval, self).write(vals)

class AccountSupplierBankCheck(models.Model):
    # Update vendor bank account in account invoice on_change checking
    
    _inherit = 'account.invoice'
        
    @api.multi
    @api.constrains('partner_id')
    def _check_partner_id(self):
        bank_list=[]
        if self.type=='in_invoice':
            partner=self.env['res.partner.bank'].search([('partner_id.id', '=', self.partner_id.id)])
            for bank in partner:
                bank_list.append(bank.state)
                if 'confirmed' not in bank_list:
                    raise UserError(_('The supplier has changed bank details which are not yet approved.'))
            
                 
            
class PaymentSupplierBankCheck(models.Model):
    
    # Update  vendor bank account in account payment checking
    
    _inherit = 'account.payment'

    @api.constrains('partner_id')
    def _check_partner_id(self):
        bank_payment_list=[]
        if self.partner_id.supplier==True:
            partner=self.env['res.partner.bank'].search([('partner_id.id', '=', self.partner_id.id)])
            for bank in partner:
                bank_payment_list.append(bank.state)
            if 'confirmed' not in bank_payment_list:
                raise UserError(_('The supplier has changed bank details which are not yet approved.'))


          


            