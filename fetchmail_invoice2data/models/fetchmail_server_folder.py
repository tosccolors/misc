# -*- coding: utf-8 -*-
# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from odoo import _, api, models, fields


class FetchmailServerFolder(models.Model):
    _inherit = 'fetchmail.server.folder'

    operating_unit_id = fields.Many2one('operating.unit',string='Operating Unit',)

    # Overridden
    @api.multi
    def attach_mail(self, match_object, mail_message):
        """Attach mail to match_object."""
        self.ensure_one()
        partner = False
        model_name = self.model_id.model
        operating_unit_id = self.operating_unit_id and self.operating_unit_id.id
        if model_name == 'res.partner':
            partner = match_object
        elif 'partner_id' in self.env[model_name]._fields:
            partner = match_object.partner_id
        attachments = []
        if self.server_id.attach and mail_message.get('attachments'):
            for attachment in mail_message['attachments']:
                # Attachment should at least have filename and data, but
                # might have some extra element(s)
                if len(attachment) < 2:
                    continue
                fname, fcontent = attachment[:2]
                if isinstance(fcontent, unicode):
                    fcontent = fcontent.encode('utf-8')
                data_attach = {
                    'name': fname,
                    'datas': base64.b64encode(str(fcontent)),
                    'datas_fname': fname,
                    'description': _('Mail attachment'),
                    'res_model': model_name,
                    'res_id': match_object.id,
                    'operating_unit_id': operating_unit_id}
                attachment = self.env['ir.attachment'].create(data_attach)
                attachments.append(attachment)

                ir_attachment_metadata = self.env['ir.attachment.metadata']
                ir_attachment_metadata.create({'attachment_id': attachment.id, 'operating_unit_id': operating_unit_id})

        self.env['mail.message'].create({
            'author_id': partner and partner.id or False,
            'model': model_name,
            'res_id': match_object.id,
            'message_type': 'email',
            'body': mail_message.get('body'),
            'subject': mail_message.get('subject'),
            'email_from': mail_message.get('from'),
            'date': mail_message.get('date'),
            'message_id': mail_message.get('message_id'),
            'attachment_ids': [(6, 0, [a.id for a in attachments])]})