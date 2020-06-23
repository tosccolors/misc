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

    @api.model
    def create(self,vals):
        operating_unit_id = self._context.get('operating_unit_id')
        res = super(IrAttachment,self).create(vals)
        # ir_attachment_metadata = self.env['ir.attachment.metadata']
        # ir_attachment_metadata.create({'attachment_id':res.id,'operating_unit_id':operating_unit_id})
        return res
        

class Message(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self,vals):
        operating_unit_id = self._context.get('operating_unit_id')
        ir_attachment = self.env['ir.attachment']
        res = super(Message,self).create(vals)

        metadata_creation_rule = self.env['mail.thread']._get_metadata_creation_rule()
        ir_attachment_metadata = self.env['ir.attachment.metadata']

        if vals.get('attachment_ids'):
            for attachment in vals.get('attachment_ids',[]):
                attachment_id = attachment[1]
                ir_attachment_ids = ir_attachment.search([('id','=',attachment_id)],limit=1)
                ir_attachment_ids.write({'mail_message_id':res.id,'operating_unit_id':operating_unit_id})

                if metadata_creation_rule == 'multiple_metadata' or metadata_creation_rule == False:
                    ir_attachment_metadata.create({'attachment_id': attachment_id, 'operating_unit_id': operating_unit_id, 'metadata_attachment': 'multiple_metadata'})

            if metadata_creation_rule == 'single_metadata':
                ir_attachment_metadata.create({'attachment_id': vals.get('attachment_ids')[0][1], 'attachment_ids': [(6, False, [attachment[1] for attachment in vals.get('attachment_ids')])], 'operating_unit_id': operating_unit_id, 'metadata_attachment': 'single_metadata'})

        return res

class IrAttachmentMetadata(models.Model):
    _inherit = ['ir.attachment.metadata']

    attachment_ids = fields.Many2many('ir.attachment', help="Link to ir.attachment models ")
    email_from = fields.Char('From', related='mail_message_id.email_from')
    metadata_attachment = fields.Selection([('single_metadata', 'All attachments into one Metadata attachment'),
                                            ('multiple_metadata', 'Each attachment into one Metadata attachment')],
                                           string="Create Metadata")