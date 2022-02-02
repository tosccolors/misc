# -*- coding: utf-8 -*-
from odoo import http

# class SupplierBankChangeApproval(http.Controller):
#     @http.route('/supplier_bank_change_approval/supplier_bank_change_approval/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/supplier_bank_change_approval/supplier_bank_change_approval/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('supplier_bank_change_approval.listing', {
#             'root': '/supplier_bank_change_approval/supplier_bank_change_approval',
#             'objects': http.request.env['supplier_bank_change_approval.supplier_bank_change_approval'].search([]),
#         })

#     @http.route('/supplier_bank_change_approval/supplier_bank_change_approval/objects/<model("supplier_bank_change_approval.supplier_bank_change_approval"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('supplier_bank_change_approval.object', {
#             'object': obj
#         })