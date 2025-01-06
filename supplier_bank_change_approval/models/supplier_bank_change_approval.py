# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class SupplierBankApproval(models.Model):
       #Update vendor bank account with states
    _inherit = 'res.partner.bank'
    
    state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed")],default='draft',string='Status', copy=False, index=True,readonly=True, store=True,track_visibility='always')
    is_supplier = fields.Boolean(related='partner_id.is_supplier', store=True)


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
        if res_partner.is_supplier:
            vals['state'] = 'draft'
        else:
            vals['state'] = 'confirmed'
        return super(SupplierBankApproval, self).create(vals)
       

    def write(self, vals):
        # Update vendor bank account then  
        # :return:state Draft
        
        if self.partner_id.is_supplier:
            if self.state == 'confirmed':
                vals.update({'state' : 'draft'})
        return super(SupplierBankApproval, self).write(vals)

class AccountInvoice(models.Model):
    # Update vendor bank account in account invoice on_change checking
    _inherit = 'account.move'
    
    @api.constrains('partner_id', 'partner_bank_id')
    def _check_partner_id(self):
        # bank_list = []
        # if self.move_type == 'in_invoice':
        #     partnerBnk = self.env['res.partner.bank'].search([('partner_id.id', '=', self.partner_id.id)])
        #     for bank in partnerBnk:
        #         bank_list.append(bank.state)
        #         if 'confirmed' not in bank_list:
        #             raise UserError(_('The supplier has changed bank details which are not yet approved.'))

        for case in self:
            if case.move_type == 'in_invoice' and case.partner_bank_id:
                # if not any(bnk.state == 'confirmed' for bnk in self.partner_id.bank_ids):
                if case.partner_bank_id.state != 'confirmed':
                    raise UserError(_("Please approve the Bank account [ %s ] to proceed further !")
                            % (case.partner_bank_id.display_name))
            
                 
            
class Payment(models.Model):
    # Update  vendor bank account in account payment checking
    _inherit = 'account.payment'

    # @api.constrains('partner_id')
    # def _check_partner_id(self):
    #     bank_payment_list = []
    #     if self.partner_id.is_supplier:
    #         partnerBnk = self.env['res.partner.bank'].search([('partner_id.id', '=', self.partner_id.id)])
    #         for bank in partnerBnk:
    #             bank_payment_list.append(bank.state)
    #         if 'confirmed' not in bank_payment_list:
    #             raise UserError(_('The supplier has changed bank details which are not yet approved.'))


    @api.constrains('partner_id', 'partner_bank_id')
    def _check_vendor_Bank(self):
        "Check if Vendor Bank account has been confirmed"
        for case in self:
            if case.partner_bank_id and self.partner_id.is_supplier:
                if case.partner_bank_id.state != 'confirmed':
                    raise ValidationError(
                        _("Please approve the Bank account [ %s ] to proceed further !")
                        % (case.partner_bank_id.display_name))

class PaymentOrder(models.Model):
    # checking bank account of Partner in account payment order
    _inherit = 'account.payment.order'
    
    # def draft2open(self):
    #     partner_ids = self.payment_line_ids.mapped('partner_id')
    #     for partner in partner_ids:
    #         partner_bank = self.env['res.partner.bank'].search([('partner_id.id', '=', partner.id)])
    #         bank_paymentorder_list = partner_bank.mapped('state')
    #         if 'confirmed' not in bank_paymentorder_list:
    #             raise UserError(_('The supplier  {0}  has added/changed bank details which are not yet approved.'.format(partner.name)))
    #     return super(PaymentOrder, self).draft2open()

    def draft2open_payment_line_check(self):
        res = super(PaymentOrder, self).draft2open_payment_line_check()

        if self.bank_account_required and self.partner_bank_id and not self.partner_bank_id.state == 'confirmed':
            raise UserError(
                _("Partner Bank Account has not been approved %s") % self.name
            )
        return res



            