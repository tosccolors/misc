# -*- coding: utf-8 -*-
from odoo import http

# class AccountingSourceDocumentAttachmentPreview(http.Controller):
#     @http.route('/accounting_source_document_attachment_preview/accounting_source_document_attachment_preview/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_source_document_attachment_preview/accounting_source_document_attachment_preview/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_source_document_attachment_preview.listing', {
#             'root': '/accounting_source_document_attachment_preview/accounting_source_document_attachment_preview',
#             'objects': http.request.env['accounting_source_document_attachment_preview.accounting_source_document_attachment_preview'].search([]),
#         })

#     @http.route('/accounting_source_document_attachment_preview/accounting_source_document_attachment_preview/objects/<model("accounting_source_document_attachment_preview.accounting_source_document_attachment_preview"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_source_document_attachment_preview.object', {
#             'object': obj
#         })