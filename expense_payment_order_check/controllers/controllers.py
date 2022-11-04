# -*- coding: utf-8 -*-
from odoo import http

# class ExpensePaymentOrderCheck(http.Controller):
#     @http.route('/expense_payment_order_check/expense_payment_order_check/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/expense_payment_order_check/expense_payment_order_check/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('expense_payment_order_check.listing', {
#             'root': '/expense_payment_order_check/expense_payment_order_check',
#             'objects': http.request.env['expense_payment_order_check.expense_payment_order_check'].search([]),
#         })

#     @http.route('/expense_payment_order_check/expense_payment_order_check/objects/<model("expense_payment_order_check.expense_payment_order_check"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('expense_payment_order_check.object', {
#             'object': obj
#         })