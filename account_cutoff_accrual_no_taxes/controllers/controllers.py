# -*- coding: utf-8 -*-
from odoo import http

# class AccountCutoffAccrualNoTaxes(http.Controller):
#     @http.route('/account_cutoff_accrual_no_taxes/account_cutoff_accrual_no_taxes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_cutoff_accrual_no_taxes/account_cutoff_accrual_no_taxes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_cutoff_accrual_no_taxes.listing', {
#             'root': '/account_cutoff_accrual_no_taxes/account_cutoff_accrual_no_taxes',
#             'objects': http.request.env['account_cutoff_accrual_no_taxes.account_cutoff_accrual_no_taxes'].search([]),
#         })

#     @http.route('/account_cutoff_accrual_no_taxes/account_cutoff_accrual_no_taxes/objects/<model("account_cutoff_accrual_no_taxes.account_cutoff_accrual_no_taxes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_cutoff_accrual_no_taxes.object', {
#             'object': obj
#         })