# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode, b64encode
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class I2dYmlTemplate(models.Model):
    _name = "i2d.yml.template"

    yml_content = fields.Text(
        string=_("YML Content"),
        required=True,
        translate=False,
        readonly=False,
        default="# -*- coding: utf-8 -*-"
    )
    name = fields.Char(
        string=_("Name"),
        required=True,
        translate=False,
        readonly=False
    )
    description = fields.Char(
        string=_("Description"),
        required=False,
        translate=False,
        readonly=False
    )
    state = fields.Selection(
        selection=[
            ('new','Not yet in File System'),
            ('saved', 'In File System'),
            ('deleted', 'Deleted from File System'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='new')
    attach_meta_id = fields.Many2one('ir.attachment.metadata', string='Attachment Meta ID')
    regexr_iframe = fields.Boolean('iFrame with regexpr hulp')

    @api.multi
    def action_export_filesystem(self):
        self.ensure_one()
        vals = {
            'task_id': self.env.ref('i2d_yml_template.i2d_yml_template_task').id,
            'file_type': 'export_external_location',
            'datas_fname': self.name +'.yml',
            'datas': b64encode(self.yml_content),
            'name': self.name,
            'description': self.description,
            'res_name': self.name,
            'res_model': 'i2d.yml.template',
            'res_id': self.id,
#                'res_field': ,
            'type': 'binary',
            'state': 'pending',
#                'state_message':,
            'mimetype': 'text/plain',
        }
        if self.state == 'new':
            res = self.env['ir.attachment.metadata'].create(vals)
            self.attach_meta_id = res.id
        if self.state in ['saved','deleted']:
            res = self.env['ir.attachment.metadata'].search([('id','=', self.attach_meta_id.id)])
            res.write(vals)
        self._cr.commit()
        res.run()
        self.write({'state': 'saved'})

    @api.multi
    def action_delete(self):
        self.ensure_one()
        if self.state == 'saved':
            vals = {
                'file_type': 'delete_external_location',
                'datas_fname': self.name + '.yml',
                'type': 'binary',
                'state': 'pending',
                #                'state_message':,
                'mimetype': 'text/plain',
            }
            if self.state == 'saved':
                res = self.env['ir.attachment.metadata'].search([('id', '=', self.attach_meta_id.id)])
                res.write(vals)
                self._cr.commit()
                res.run()
                self.write({'state': 'deleted'})

    @api.multi
    def unlink(self):
        if self.state == 'saved':
            raise UserError(_('This YML temlate is still present in the filesystem. You first have to delete it there'))
        super(I2dYmlTemplate, self).unlink()