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
            if self.partner_bank_id.id:
                self.copy_record=False
        return
            
#    Update the duplicate of vendor invoice partner_bank_id into empty if it not link with res.partner and set copy_record into True
    
    @api.multi   
    def copy(self, default):
        default = dict(default or {})
        if self.type=='in_invoice':
            if self.partner_bank_id.id != False and self.partner_bank_id.partner_id.id==False:
                default.update({'partner_bank_id':False,'copy_record':True})  
        return super(InvoiceDuplicationBankCheck, self).copy(default)            
    
                     
    #  validating the partner_bank_id is link to res.partner           
            
    def invoice_validate(self):
        if self.type=='in_invoice':
            if self.partner_bank_id.id != False and self.partner_bank_id.partner_id.id==False:
                raise UserError('The partner bank details have changed. Check the bank details')                  
        return super(InvoiceDuplicationBankCheck, self).invoice_validate()

    