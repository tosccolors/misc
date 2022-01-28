# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.one
    def _check_approver(self):
        approver = False
        expOfficer = self.env.user.has_group('hr_expense.group_hr_expense_user')
        if self.env.uid != self.create_uid.id and expOfficer and self.state == 'submit':
            approver = True
        self.is_approver = approver

    is_approver = fields.Boolean(string="Is Approver", compute='_check_approver')


