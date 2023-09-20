# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    
    def link_bank_to_partner(self):
        """
        overiden link_bank_to_partner() to skip updating iban for supplier
        :return:
        """
        for statement in self:
            for st_line in statement.line_ids:
                if st_line.bank_account_id and st_line.partner_id and not st_line.partner_id.supplier and st_line.bank_account_id.partner_id != st_line.partner_id:
                    st_line.bank_account_id.partner_id = st_line.partner_id