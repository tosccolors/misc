# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceLineRevenueDistributionOperatingUnit(http.Controller):
#     @http.route('/invoice_line_revenue_distribution_operating_unit/invoice_line_revenue_distribution_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_line_revenue_distribution_operating_unit/invoice_line_revenue_distribution_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_line_revenue_distribution_operating_unit.listing', {
#             'root': '/invoice_line_revenue_distribution_operating_unit/invoice_line_revenue_distribution_operating_unit',
#             'objects': http.request.env['invoice_line_revenue_distribution_operating_unit.invoice_line_revenue_distribution_operating_unit'].search([]),
#         })

#     @http.route('/invoice_line_revenue_distribution_operating_unit/invoice_line_revenue_distribution_operating_unit/objects/<model("invoice_line_revenue_distribution_operating_unit.invoice_line_revenue_distribution_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_line_revenue_distribution_operating_unit.object', {
#             'object': obj
#         })