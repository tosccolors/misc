# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceDuplicationBankAccountCheck(http.Controller):
#     @http.route('/invoice_duplication_bank_account_check/invoice_duplication_bank_account_check/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_duplication_bank_account_check/invoice_duplication_bank_account_check/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_duplication_bank_account_check.listing', {
#             'root': '/invoice_duplication_bank_account_check/invoice_duplication_bank_account_check',
#             'objects': http.request.env['invoice_duplication_bank_account_check.invoice_duplication_bank_account_check'].search([]),
#         })

#     @http.route('/invoice_duplication_bank_account_check/invoice_duplication_bank_account_check/objects/<model("invoice_duplication_bank_account_check.invoice_duplication_bank_account_check"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_duplication_bank_account_check.object', {
#             'object': obj
#         })