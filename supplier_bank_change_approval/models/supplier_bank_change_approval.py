# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SupplierBankApproval(models.Model):
   
       #Update vendor bank account with states 
    
    _inherit = 'res.partner.bank'
    
    state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed")],default='draft',string='Status', copy=False, index=True,readonly=True, store=True,track_visibility='always')
    
    def action_draft(self):
        self.state = 'draft'

    
    def action_confirm(self):
        self.state = 'confirmed'

    @api.model
    def create(self, vals):
        # Update customer bank account then
        # :return:state confirmed
        partner = vals.get('partner_id')
        res_partner = self.env['res.partner'].search([('id', '=', partner)])
        if res_partner.supplier == True:
            vals['state'] = 'draft'
        else:
            vals['state'] = 'confirmed'
        return super(SupplierBankApproval, self).create(vals)
       

    
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

class PaymentOrderBankCheck(models.Model):

    # checking bank account of Partner in account payment order

    _inherit = 'account.payment.order'

    
    def draft2open(self):
        partner_ids=self.payment_line_ids.mapped('partner_id')
        for partner in partner_ids:
            partner_bank = self.env['res.partner.bank'].search([('partner_id.id', '=', partner.id)])
            bank_paymentorder_list = partner_bank.mapped('state')
            if 'confirmed' not in bank_paymentorder_list:
                raise UserError(_('The supplier  {0}  has changed bank details which are not yet approved.'.format(partner.name)))
        return super(PaymentOrderBankCheck, self).draft2open()
          


            