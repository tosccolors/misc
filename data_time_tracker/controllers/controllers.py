# -*- coding: utf-8 -*-
from odoo import http

# class DataTimeTracker(http.Controller):
#     @http.route('/data_time_tracker/data_time_tracker/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/data_time_tracker/data_time_tracker/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('data_time_tracker.listing', {
#             'root': '/data_time_tracker/data_time_tracker',
#             'objects': http.request.env['data_time_tracker.data_time_tracker'].search([]),
#         })

#     @http.route('/data_time_tracker/data_time_tracker/objects/<model("data_time_tracker.data_time_tracker"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('data_time_tracker.object', {
#             'object': obj
#         })