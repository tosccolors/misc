# -*- coding: utf-8 -*-
from odoo import models, fields, _
from odoo.exceptions import UserError


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    def _prepare_tax_lines(self, tax_compute_all_res, currency):
        res = []
        if self.company_id.accrual_no_taxes and \
                self.type in ['accrued_expense', 'accrued_revenue']:
            return res
        return super(AccountCutoff, self)._prepare_tax_lines(tax_compute_all_res, currency)