# coding: utf-8
# @ 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64decode
import hashlib
import logging
import odoo 
from odoo import _, api, fields, models
from odoo.exceptions import UserError
# import PyPDF2 
# import json
# import tabula
_logger = logging.getLogger(__name__)


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    mail_message_id = fields.Many2one("mail.message","Mail Message ID")

    @api.model
    def create(self,vals):
        res = super(IrAttachment,self).create(vals)
        ir_attachment_metadata = self.env['ir.attachment.metadata']
        ir_attachment_metadata.create({'attachment_id':res.id})
        return res
        

class Message(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self,vals):
        ir_attachment = self.env['ir.attachment']
        res = super(Message,self).create(vals)
        if vals.get('attachment_ids'):
            for attachment in vals.get('attachment_ids',[]):
                attachment_id = attachment[1]
                ir_attachment_ids = ir_attachment.search([('id','=',attachment_id)],limit=1)
                ir_attachment_ids.write({'mail_message_id':res.id})
        return res
    
    
#     @api.multi
#     def open_attachment(self):
#         
#         mail_message_ids = self.search([])
#         ir_attachment_metadata  = self.env['ir.attachment.metadata']
#         for mail in mail_message_ids:
#             attachments = ir_attachment_metadata.search([('mail_message_id','=',mail.id),('id','=',25)])
#             for attachment in attachments:
#                 df = tabula.read_pdf(attachment.local_url, output_format="json", pages="all")
#                 print("Attachment is here....",attachment.local_url) 
                