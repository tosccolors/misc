# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools.translate import _


class I2dYmlTemplate(models.Model):
    _name = "i2d.yml.template"

    yml_content = fields.Text(
        string=_("YML Content"),
        required=True,
        translate=False,
        readonly=False
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

    @api.multi
    def action_export_filesystem(self):
        self.ensure_one()
        if self.state in ['new','saved']:
            vals = {
                'task_id': 'i2d yml export',
                'file_type': 'export_external_location',
                'datas_fname': self.name +'.yml',
                'datas': self.yml_content,
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
                self.env['ir.attachment.metadata'].create(vals)
            if self.state == 'saved':
                self.env['ir.attachment.metadata'].write(vals)
            self.write({'state': 'saved'})

    @api.multi
    def action_delete(self):
        self.ensure_one()
        if self.state == 'saved':
            vals = {
                'task_id': 'i2d yml export',
                'file_type': 'delete_external_location',
                'datas_fname': self.name + '.yml',
                'type': 'binary',
                'state': 'pending',
                #                'state_message':,
                'mimetype': 'text/plain',
            }
            if self.state == 'saved':
                self.env['ir.attachment.metadata'].write(vals)
                self.write({'state': 'deleted'})