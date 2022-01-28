# -*- coding: utf-8 -*-
from odoo import http

# class CrmActivityAddon(http.Controller):
#     @http.route('/crm_activity_addon/crm_activity_addon/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_activity_addon/crm_activity_addon/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_activity_addon.listing', {
#             'root': '/crm_activity_addon/crm_activity_addon',
#             'objects': http.request.env['crm_activity_addon.crm_activity_addon'].search([]),
#         })

#     @http.route('/crm_activity_addon/crm_activity_addon/objects/<model("crm_activity_addon.crm_activity_addon"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_activity_addon.object', {
#             'object': obj
#         })