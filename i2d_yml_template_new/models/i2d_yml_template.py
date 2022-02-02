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
        readonly=False,
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
    attach_meta_id = fields.Many2one('attachment.queue', string='Attachment Meta ID')
    regexr_iframe = fields.Boolean('iFrame with regexpr hulp')
    partner_ids = fields.One2many('yml.template.partner', 'template_id', string='Template Vendors', copy=True)


    @api.multi
    @api.onchange('partner_id' )
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Name
        """
        if self.partner_id and not self.name:
            self.name = self.partner_id.name

    @api.multi
    def action_export_filesystem(self):
        self.ensure_one()
        vals = {
            'task_id': self.env.ref('i2d_yml_template_new.i2d_yml_template_task').id,
            'file_type': 'export_external_location',
            'datas_fname': self.name +'.yml',
            'datas': b64encode(self.yml_content.encode('utf8')),
            'name': self.name,
            'description': self.description,
            'res_name': self.name,
            'res_model': 'i2d.yml.template',
            'res_id': self.id,
            'type': 'binary',
            'state': 'pending',
            'mimetype': 'text/plain',
        }
        if self.state == 'new':
            res = self.env['attachment.queue'].create(vals)
            self.attach_meta_id = res.id
        if self.state in ['saved','deleted']:
            res = self.env['attachment.queue'].search([('id','=', self.attach_meta_id.id)])
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
                'mimetype': 'text/plain',
            }
            if self.state == 'saved':
                res = self.env['attachment.queue'].search([('id', '=', self.attach_meta_id.id)])
                res.write(vals)
                self._cr.commit()
                res.run()
                self.write({'state': 'deleted'})

    @api.multi
    def unlink(self):
        for tmpl in self:
            if self.state == 'saved':
                tmpl.action_delete()
        super(I2dYmlTemplate, self).unlink()


class YmlTemplatePartner(models.Model):
    _name = "yml.template.partner"

    template_id = fields.Many2one('i2d.yml.template', string='Template')
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 domain=[('supplier', '=', True), ('is_company', '=', True)])
    partner_vat = fields.Char(related='partner_id.vat', string='VAT of Vendor')
    invoice_import_ids = fields.One2many('account.invoice.import.config',
                                        related='partner_id.invoice_import_ids', )
    company_id = fields.Many2one('res.company', related='partner_id.company_id', string='Partner Company')