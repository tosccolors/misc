# -*- coding: utf-8 -*-
# from odoo import http


# class UserManagement(http.Controller):
#     @http.route('/user_management/user_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/user_management/user_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('user_management.listing', {
#             'root': '/user_management/user_management',
#             'objects': http.request.env['user_management.user_management'].search([]),
#         })

#     @http.route('/user_management/user_management/objects/<model("user_management.user_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('user_management.object', {
#             'object': obj
#         })
