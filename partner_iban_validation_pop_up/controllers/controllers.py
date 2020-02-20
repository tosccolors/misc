# -*- coding: utf-8 -*-
from odoo import http

# class PartnerIbanValidationPopUp(http.Controller):
#     @http.route('/partner_iban_validation_pop_up/partner_iban_validation_pop_up/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_iban_validation_pop_up/partner_iban_validation_pop_up/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_iban_validation_pop_up.listing', {
#             'root': '/partner_iban_validation_pop_up/partner_iban_validation_pop_up',
#             'objects': http.request.env['partner_iban_validation_pop_up.partner_iban_validation_pop_up'].search([]),
#         })

#     @http.route('/partner_iban_validation_pop_up/partner_iban_validation_pop_up/objects/<model("partner_iban_validation_pop_up.partner_iban_validation_pop_up"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_iban_validation_pop_up.object', {
#             'object': obj
#         })