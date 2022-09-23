# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('move_id.line_ids.payment_line_ids')
    @api.multi
    def _compute_payment_order(self):
        payment_order_line = self.env['account.payment.line']
        for inv in self.filtered(lambda n: n.type == 'in_invoice'):
            pol = payment_order_line.search([('move_line_id', 'in', inv.move_id.line_ids.ids)])
            payment_order = pol.mapped('order_id')
            inv.invoice_payment_order_id = payment_order and payment_order.ids[0] or payment_order

    invoice_payment_order_id = fields.Many2one('account.payment.order', 'Payment Order',
                                       compute="_compute_payment_order", store=True)
