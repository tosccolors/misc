# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError



class InvoiceDuplicationBankCheck(models.Model):
    _inherit='account.invoice'

    copy_record = fields.Boolean()
     
      
    # check duplicate vendor invoice have the partner_bank_details

    @api.onchange('copy_record','partner_bank_id')
    def _onchange_copy_record(self):
        if self.type=='in_invoice':
            if self.partner_bank_id:
                self.copy_record=False
        return
            
#    Update the duplicate of vendor invoice partner_bank_id into empty if it not link with res.partner and set copy_record into True
    
    def copy(self, default):
        default = dict(default or {})
        if self.type=='in_invoice' or self.type=='in_refund':
            if self.partner_bank_id and not self.partner_bank_id.partner_id:
                default.update({'partner_bank_id':False,'copy_record':True})
            elif self.partner_bank_id and self.partner_bank_id.partner_id and self.partner_bank_id.partner_id.id != self.partner_id.id:
                default.update({'partner_bank_id': False, 'copy_record': True})
        return super(InvoiceDuplicationBankCheck, self).copy(default)
    
                     
    #  validating the partner_bank_id is link to res.partner
    def invoice_validate(self):
        if self.type=='in_invoice'  or self.type=='in_refund' :
            if self.partner_bank_id and not self.partner_bank_id.partner_id:
                raise UserError('The partner bank details have changed. Check the bank details')
            elif self.partner_bank_id and self.partner_bank_id.partner_id and self.partner_bank_id.partner_id.id != self.partner_id.id:
                raise UserError('The bank account partner for this invoice is not the same as the partner in the bank account',)
        return super(InvoiceDuplicationBankCheck, self).invoice_validate()

    @api.constrains('partner_bank_id')
    def check_partner_bank_id(self):
        if self.type=='in_invoice'  or self.type=='in_refund' :
            if self.partner_bank_id and not self.partner_bank_id.partner_id:
                raise ValidationError('The partner bank details have changed. Check the bank details')
            elif self.partner_bank_id and self.partner_bank_id.partner_id and self.partner_bank_id.partner_id.id != self.partner_id.id:
                raise ValidationError('The bank account partner for this invoice is not the same as the partner in the bank account')
        return True



    