# -*- coding: utf-8 -*-
from odoo import http

# class SupplierIbanIgnoreBankStatementUpdate(http.Controller):
#     @http.route('/supplier_iban_ignore_bank_statement_update/supplier_iban_ignore_bank_statement_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/supplier_iban_ignore_bank_statement_update/supplier_iban_ignore_bank_statement_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('supplier_iban_ignore_bank_statement_update.listing', {
#             'root': '/supplier_iban_ignore_bank_statement_update/supplier_iban_ignore_bank_statement_update',
#             'objects': http.request.env['supplier_iban_ignore_bank_statement_update.supplier_iban_ignore_bank_statement_update'].search([]),
#         })

#     @http.route('/supplier_iban_ignore_bank_statement_update/supplier_iban_ignore_bank_statement_update/objects/<model("supplier_iban_ignore_bank_statement_update.supplier_iban_ignore_bank_statement_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('supplier_iban_ignore_bank_statement_update.object', {
#             'object': obj
#         })