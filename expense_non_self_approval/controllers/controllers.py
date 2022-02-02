# -*- coding: utf-8 -*-
from odoo import http

# class ExpenseNonSelfApproval(http.Controller):
#     @http.route('/expense_non_self_approval/expense_non_self_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/expense_non_self_approval/expense_non_self_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('expense_non_self_approval.listing', {
#             'root': '/expense_non_self_approval/expense_non_self_approval',
#             'objects': http.request.env['expense_non_self_approval.expense_non_self_approval'].search([]),
#         })

#     @http.route('/expense_non_self_approval/expense_non_self_approval/objects/<model("expense_non_self_approval.expense_non_self_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('expense_non_self_approval.object', {
#             'object': obj
#         })