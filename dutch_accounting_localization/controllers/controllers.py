# -*- coding: utf-8 -*-
from odoo import http

# class DutchAccountingLocalization(http.Controller):
#     @http.route('/dutch_accounting_localization/dutch_accounting_localization/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/dutch_accounting_localization/dutch_accounting_localization/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('dutch_accounting_localization.listing', {
#             'root': '/dutch_accounting_localization/dutch_accounting_localization',
#             'objects': http.request.env['dutch_accounting_localization.dutch_accounting_localization'].search([]),
#         })

#     @http.route('/dutch_accounting_localization/dutch_accounting_localization/objects/<model("dutch_accounting_localization.dutch_accounting_localization"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('dutch_accounting_localization.object', {
#             'object': obj
#         })