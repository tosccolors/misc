# -*- coding: utf-8 -*-
from odoo import http

# class SupplierIbanRecursiveChange(http.Controller):
#     @http.route('/supplier_iban_recursive_change/supplier_iban_recursive_change/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/supplier_iban_recursive_change/supplier_iban_recursive_change/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('supplier_iban_recursive_change.listing', {
#             'root': '/supplier_iban_recursive_change/supplier_iban_recursive_change',
#             'objects': http.request.env['supplier_iban_recursive_change.supplier_iban_recursive_change'].search([]),
#         })

#     @http.route('/supplier_iban_recursive_change/supplier_iban_recursive_change/objects/<model("supplier_iban_recursive_change.supplier_iban_recursive_change"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('supplier_iban_recursive_change.object', {
#             'object': obj
#         })