# -*- coding: utf-8 -*-

from odoo import models, api, tools, fields, _
from odoo.exceptions import UserError

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    standard = fields.Boolean('Is Stanadrad Account?')

    @api.multi
    @api.constrains('standard', 'partner_id', 'company_id')
    def _check_company(self):
        for res in self:
            standard_accs = self.search([('standard', '=', True), ('partner_id', '=', res.partner_id.id), ('company_id', '=', res.company_id.id)])
            if len(standard_accs) > 1:
                raise UserError(_('Configuration error!\nThere must be only one standard account belongs to each account holder and company.'))


    @api.multi
    def update_supplier_bill_bank_account(self):
        """
        Update unpaid vendor bills with standard bank account
        :return:
        """
        self._cr.execute("""
                 UPDATE account_invoice
                 SET partner_bank_id = %s
                 WHERE type IN ('in_invoice', 'in_refund')
                 AND company_id= %s
                 AND partner_id= %s
                 AND state NOT IN ('paid', 'cancel')
                 """, (self.id, self.company_id.id, self.partner_id.id)
            )

    @api.multi
    def update_payment_order_lines(self):
        """
        Update draft payment order with standard bank account
        :return:
        """
        self._cr.execute("""
                 UPDATE account_payment_line
                 SET partner_bank_id = %s
                 WHERE order_id IN (
                          SELECT id FROM account_payment_order 
                          WHERE state = 'draft' 
                          AND payment_type = 'outbound'                      
                    ) 
                 AND company_id= %s            
                 AND partner_id= %s           
                 """, (self.id, self.company_id.id, self.partner_id.id)
             )


    @api.model
    def create(self, vals):
        res = super(ResPartnerBank, self).create(vals)
        if res.standard:
            res.update_supplier_bill_bank_account()
            res.update_payment_order_lines()
        return res

    @api.multi
    def write(self, vals):
        result = super(ResPartnerBank, self).write(vals)
        if vals.get('standard', False):
            for res in self:
                res.update_supplier_bill_bank_account()
                res.update_payment_order_lines()
        return result