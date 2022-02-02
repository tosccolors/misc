# -*- coding: utf-8 -*-
from odoo import http

# class OcaReportOperatingUnit(http.Controller):
#     @http.route('/oca_report_operating_unit/oca_report_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oca_report_operating_unit/oca_report_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oca_report_operating_unit.listing', {
#             'root': '/oca_report_operating_unit/oca_report_operating_unit',
#             'objects': http.request.env['oca_report_operating_unit.oca_report_operating_unit'].search([]),
#         })

#     @http.route('/oca_report_operating_unit/oca_report_operating_unit/objects/<model("oca_report_operating_unit.oca_report_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oca_report_operating_unit.object', {
#             'object': obj
#         })