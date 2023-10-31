# -*- coding: utf-8 -*-
from odoo import http

# class MontaDeliveryOrder(http.Controller):
#     @http.route('/monta_delivery_order/monta_delivery_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/monta_delivery_order/monta_delivery_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('monta_delivery_order.listing', {
#             'root': '/monta_delivery_order/monta_delivery_order',
#             'objects': http.request.env['monta_delivery_order.monta_delivery_order'].search([]),
#         })

#     @http.route('/monta_delivery_order/monta_delivery_order/objects/<model("monta_delivery_order.monta_delivery_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('monta_delivery_order.object', {
#             'object': obj
#         })