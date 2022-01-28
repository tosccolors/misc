# -*- coding: utf-8 -*-
from odoo import http

# class IntrastatOperatingUnit(http.Controller):
#     @http.route('/intrastat_operating_unit/intrastat_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/intrastat_operating_unit/intrastat_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('intrastat_operating_unit.listing', {
#             'root': '/intrastat_operating_unit/intrastat_operating_unit',
#             'objects': http.request.env['intrastat_operating_unit.intrastat_operating_unit'].search([]),
#         })

#     @http.route('/intrastat_operating_unit/intrastat_operating_unit/objects/<model("intrastat_operating_unit.intrastat_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('intrastat_operating_unit.object', {
#             'object': obj
#         })