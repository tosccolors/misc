# -*- coding: utf-8 -*-
from odoo import http

# class CrmActivityAddonSimplified(http.Controller):
#     @http.route('/crm_activity_addon_simplified/crm_activity_addon_simplified/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_activity_addon_simplified/crm_activity_addon_simplified/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_activity_addon_simplified.listing', {
#             'root': '/crm_activity_addon_simplified/crm_activity_addon_simplified',
#             'objects': http.request.env['crm_activity_addon_simplified.crm_activity_addon_simplified'].search([]),
#         })

#     @http.route('/crm_activity_addon_simplified/crm_activity_addon_simplified/objects/<model("crm_activity_addon_simplified.crm_activity_addon_simplified"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_activity_addon_simplified.object', {
#             'object': obj
#         })