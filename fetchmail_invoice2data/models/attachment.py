# coding: utf-8
# @ 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64decode
import hashlib
import logging
import odoo 
from odoo import _, api, fields, models
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    mail_message_id = fields.Many2one("mail.message","Mail Message ID")
    operating_unit_id = fields.Many2one('operating.unit',string='Operating Unit',)
        

class Message(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self,vals):
        ir_attachment = self.env['ir.attachment']
        res = super(Message,self).create(vals)

        if vals.get('attachment_ids'):
            for attachment in vals.get('attachment_ids',[])[0][2]:
                attachment_id = attachment
                ir_attachment_ids = ir_attachment.search([('id','=',attachment_id)],limit=1)
                ir_attachment_ids.write({'mail_message_id':res.id})
        return res

class IrAttachmentMetadata(models.Model):
    _inherit = ['attachment.queue']

    attachment_ids = fields.Many2many('ir.attachment', help="Link to ir.attachment models ")
    email_from = fields.Char('From', related='mail_message_id.email_from')
    metadata_attachment = fields.Selection([('single_metadata', 'All attachments into one Metadata attachment'),
                                            ('multiple_metadata', 'Each attachment into one Metadata attachment')],
                                           string="Create Metadata")