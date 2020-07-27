# -*- coding: utf-8 -*-
from odoo import http

# class AccountReversalViaSql(http.Controller):
#     @http.route('/account_reversal_via_sql/account_reversal_via_sql/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_reversal_via_sql/account_reversal_via_sql/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_reversal_via_sql.listing', {
#             'root': '/account_reversal_via_sql/account_reversal_via_sql',
#             'objects': http.request.env['account_reversal_via_sql.account_reversal_via_sql'].search([]),
#         })

#     @http.route('/account_reversal_via_sql/account_reversal_via_sql/objects/<model("account_reversal_via_sql.account_reversal_via_sql"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_reversal_via_sql.object', {
#             'object': obj
#         })