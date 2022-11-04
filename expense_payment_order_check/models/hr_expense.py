# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.depends('account_move_id.line_ids.payment_line_ids')
    @api.multi
    def _compute_payment_order(self):
        payment_order_line = self.env['account.payment.line']
        for exp in self:
            pol = payment_order_line.search([('move_line_id', 'in', exp.account_move_id.line_ids.ids)])
            payment_order = pol.mapped('order_id')
            exp.expense_payment_order_id = payment_order and payment_order.ids[0] or payment_order

    expense_payment_order_id = fields.Many2one('account.payment.order', 'Payment Order',
                                       compute="_compute_payment_order", store=True)
