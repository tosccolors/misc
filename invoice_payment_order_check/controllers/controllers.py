# -*- coding: utf-8 -*-
from odoo import http

# class InvoicePaymentOrderView(http.Controller):
#     @http.route('/invoice_payment_order_view/invoice_payment_order_view/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_payment_order_view/invoice_payment_order_view/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_payment_order_view.listing', {
#             'root': '/invoice_payment_order_view/invoice_payment_order_view',
#             'objects': http.request.env['invoice_payment_order_view.invoice_payment_order_view'].search([]),
#         })

#     @http.route('/invoice_payment_order_view/invoice_payment_order_view/objects/<model("invoice_payment_order_view.invoice_payment_order_view"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_payment_order_view.object', {
#             'object': obj
#         })