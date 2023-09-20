# -*- coding: utf-8 -*-
from odoo import http

# class WriteoffOperatingUnit(http.Controller):
#     @http.route('/writeoff_operating_unit/writeoff_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/writeoff_operating_unit/writeoff_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('writeoff_operating_unit.listing', {
#             'root': '/writeoff_operating_unit/writeoff_operating_unit',
#             'objects': http.request.env['writeoff_operating_unit.writeoff_operating_unit'].search([]),
#         })

#     @http.route('/writeoff_operating_unit/writeoff_operating_unit/objects/<model("writeoff_operating_unit.writeoff_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('writeoff_operating_unit.object', {
#             'object': obj
#         })