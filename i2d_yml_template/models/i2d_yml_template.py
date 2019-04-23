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
        default="# -*- coding: utf-8 -*-\n\
issuer: MySupplier \n\
fields: \n\
  amount: Totaalbedrag\x3A\s+(\d{0,3}\.{0,1}\d{1,3},\d{2}) EUR\n\
  amount_untaxed: Netto\x3A\s+(\d{0,3}\.{0,1}\d{1,3},\d{2}) EUR\n\
  date: Factuurdatum\x3A\s+{1,8}\s+(\d{1,2}-\d{1,2}-\d{4})\n\
  invoice_number: Factuurnummer\x3A\s+(\d{0,7})\n\
  static_vat: NL123456\n\
  description: Omschrijving (.*)\n\
keywords:\n\
    - 'KvK nummer 123456789'\n\
options:\n\
  currency: EUR\n\
  date_formats:\n\
    - '%d-%m-%Y'\n\
  languages:\n\
    - nl\n\
  decimal_separator: ','"
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
    attach_meta_id = fields.Many2one('ir.attachment.metadata', string='Attachment Meta ID')
    regexr_iframe = fields.Boolean('iFrame with regexpr hulp')
    partner_ids = fields.One2many('yml.template.partner', 'template_id', string='Template Vendors', copy=True)


    @api.multi
    def convert2regex(self, string2convert):
        #escape the special meaning characters (this is incomplete but sufficient to start with)
        replacements =[ ('\\', '\\\\' ), 
                        (r'*', r'\*'),
                      ]
        for replacement in replacements :
                string2convert=string2convert.replace(replacement[0], replacement[1])
        #find the substrings and replace by a regex
        keys = [r'\s+',                             #first white space
                r'\d{0,3}\.{0,1}\d{1,3},\d{2}',     #amounts have a comma
                r'\d{1,2}-\d{1,2}-\d{4}',           #specific date type can be distinguished from long numbers
                r'\d{1,2}\.\d{1,2}\.\d{4}',         #date with a point
                r'\d{5,10}',                        #remaining long numbers
                ]
        for key in keys :
            string2convert = re.sub(key, key, string2convert)
        #remove all brackets and place on set on begin and end
        string2convert.replace( '(', '')
        string2convert.replace( ')', '')
        string2convert = '('+ string2convert + ')'
        return string2convert

    @api.multi
    def keyword2regex(self):
        self.keyword = self.convert2regex(self.keyword)
        self.onchange_keyword()
        return

    @api.multi
    def amount2regex(self):
        self.amount = self.convert2regex(self.amount)
        self.onchange_amount()
        return

    @api.multi
    def amount_untaxed2regex(self):
        self.amount_untaxed = self.convert2regex(self.amount_untaxed)
        self.onchange_amount_untaxed()
        return

    @api.multi
    def date2regex(self):
        self.date = self.convert2regex(self.date)
        self.onchange_date()
        return

    @api.multi
    def invoice_number2regex(self):
        self.invoice_number = self.convert2regex(self.invoice_number)
        self.onchange_invoice_number()
        return

    @api.multi
    def description2regex(self):
        self.description = self.convert2regex(self.description)
        self.onchange_description()
        return

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
            'task_id': self.env.ref('i2d_yml_template.i2d_yml_template_task').id,
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
    invoice_import_id = fields.Many2one('account.invoice.import.config', related='partner_id.invoice_import_id', )
    company_id = fields.Many2one('res.company', related='partner_id.company_id', string='Partner Company')