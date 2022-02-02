# -*- coding: utf-8 -*-
from odoo import http

# class ContractManagement(http.Controller):
#     @http.route('/contract_management/contract_management/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_management/contract_management/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_management.listing', {
#             'root': '/contract_management/contract_management',
#             'objects': http.request.env['contract_management.contract_management'].search([]),
#         })

#     @http.route('/contract_management/contract_management/objects/<model("contract_management.contract_management"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_management.object', {
#             'object': obj
#         })