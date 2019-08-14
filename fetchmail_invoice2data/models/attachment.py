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
        ir_attachment_metadata = self.env['ir.attachment.metadata']
        ir_attachment_metadata.create({'attachment_id':res.id,'operating_unit_id':operating_unit_id})
        return res
        

class Message(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self,vals):
        operating_unit_id = self._context.get('operating_unit_id')
        ir_attachment = self.env['ir.attachment']
        res = super(Message,self).create(vals)
        if vals.get('attachment_ids'):
            for attachment in vals.get('attachment_ids',[]):
                attachment_id = attachment[1]
                ir_attachment_ids = ir_attachment.search([('id','=',attachment_id)],limit=1)
                ir_attachment_ids.write({'mail_message_id':res.id,'operating_unit_id':operating_unit_id})
        return res
    