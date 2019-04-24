# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode, b64encode
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.tools import config
from odoo.exceptions import UserError, Warning
from subprocess import Popen, PIPE
import os, re, tempfile
import invoice2data


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
    regexr_iframe  = fields.Boolean('iFrame with regexpr hulp')
    partner_ids    = fields.One2many('yml.template.partner', 'template_id', string='Template Vendors', copy=True)
    example_pdf    = fields.Many2many('ir.attachment', string='Example pdf')
    hide_pdf       = fields.Boolean('Hide parsed pdf', default=True)
    parsed_pdf     = fields.Text(string='Parsed pdf', compute_sudo='onchange_example_pdf', store=True)
    hide_output    = fields.Boolean('Hide test output', default=True)
    test_output    = fields.Text(string='Test output')

    keyword                = fields.Char('Keyword', help='Enter regex for field keyword, without brackets')
    keyword_result         = fields.Char('Regex result for keyword')
    amount                 = fields.Char('Amount', help='Enter regex for field amount. Don\'t forget the brackets.')
    amount_result          = fields.Char('Regex result for amount')
    amount_untaxed         = fields.Char('Amount_untaxed', help='Enter regex for field amount_untaxed. Don\'t forget the brackets.')
    amount_untaxed_result  = fields.Char('Regex result for amount_untaxed')
    date                   = fields.Char('Date', help='Enter regex for field date. Don\'t forget the brackets.')
    date_result            = fields.Char('Regex result for date')
    invoice_number         = fields.Char('Invoice number', help='Enter regex for field in=voice_number. Don\'t forget the brackets.')
    invoice_number_result  = fields.Char('Regex result for invoice_number')
    description            = fields.Char('Description', help='Enter regex for field in=description. Don\'t forget the brackets.')
    description_result     = fields.Char('Regex result for description')
    static_vat             = fields.Char('Static VAT', help='Fixed VAT number')

    @api.multi
    def show_parsed_pdf(self):
        if not self.example_pdf :
            raise UserError(_("Nothing to show. Add an example pdf first."))
            return 
        if len(self.example_pdf)>1 :
            raise UserError(_("You have more than one pdf. Remove excess attachments in example pdf."))
            return 
        self.ensure_one()
        self.hide_pdf = False
        self.onchange_example_pdf()
        return

    @api.multi
    def hide_parsed_pdf(self):
        self.ensure_one()
        self.hide_pdf = True
        return

    @api.multi
    def show_regex_configurator(self):
        self.ensure_one()
        self.regexr_iframe = True
        return

    @api.multi
    def hide_regex_configurator(self):
        self.ensure_one()
        self.regexr_iframe = False
        return

    @api.multi
    def show_test_output(self):
        self.ensure_one()
        self.hide_output = False
        self.onchange_example_pdf()
        return

    @api.multi
    def hide_test_output(self):
        self.ensure_one()
        self.hide_output = True
        self.onchange_example_pdf()

    @api.multi
    def test_yml_template(self):
        if not self.state == 'saved' :
            raise UserError(_("Please save template in external system first")) 
            self.test_output=""
            return
        if not self.example_pdf :
            raise UserError(_("No pdf to test with. Add an example pdf first."))
            self.test_output=""
            return 
        if len(self.example_pdf)>1 :
            raise UserError(_("Testing only possible with one and only one pdf. Remove excess attachments in example pdf."))
            return 
        #all ok
        data = b64decode(self.example_pdf.datas)
        fd, pdf_file = tempfile.mkstemp(suffix="pdf")
        os.write(fd, data)
        os.close(fd)
        local_templates_dir = config.get('invoice2data_templates_dir', False)
        if local_templates_dir :
            process = Popen (['invoice2data', '--debug', '--template-folder', local_templates_dir, pdf_file], shell=False, stdout=PIPE, stderr=PIPE)
        else :
            process = Popen (['invoice2data', '--debug', pdf_file], shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if not local_templates_dir :
            stderr += "Templates directory not found, check odoo.cfg and directories for correct \'invoice2data_templates_dir\'"
        self.test_output = stdout+'\n'+stderr
        #test if current pdf delivers desired keyword
        keyword_found = re.search("DEBUG:root:keywords=\['(.*)'\]", self.test_output)
        if keyword_found and self.keyword_result :
            if keyword_found.group(1) != self.keyword_result :
                #keep result by commit before user warning
                self.env.cr.commit()
                raise Warning(_("PDF matches other template than you are working on!\n"
                                +"Your template uses %s and the template found uses %s." % (self.keyword_result, keyword_found.group(1))))
        return

    @api.multi
    def compose_yml_template(self):
        if not self.keyword and not self.amount and not self.amount_untaxed and not self.date and not self.invoice_number and not self.description :
            raise UserError(_("No regex formulas entered. Nothing to compose with."))
            return 
        if len(self.partner_ids)==0 :
            raise UserError(_("Need at least one vendor associated with this template."))
            return 
        #all ok
        name = self.partner_ids[0].partner_id.name
        self.yml_content="# -*- coding: utf-8 -*-\n\
issuer: "+name+" \n\
fields:\n"
        if self.amount :
            self.yml_content += "  amount: "+self.amount+"\n"
        if self.amount_untaxed : 
            self.yml_content += "  amount_untaxed: "+self.amount_untaxed+"\n" 
        if self.date :
            self.yml_content += "  date: "+self.date+"\n"
        if self.invoice_number :
            self.yml_content += "  invoice_number: "+self.invoice_number+"\n"
        if self.static_vat :
            self.yml_content += "  static_vat: "+self.statict_vat+"\n"
        if self.description :
            self.yml_content += "  description: "+self.description+"\n"
        if self.keyword :
            self.yml_content += "keywords:\n\
    - \'"+self.keyword+"\'\n"
        self.yml_content     += "\
options:\n\
  currency: EUR\n\
  date_formats:\n\
    - '%d-%m-%Y'\n\
  languages:\n\
    - nl\n\
  decimal_separator: ','"
        return


    @api.multi
    @api.onchange('example_pdf')
    def onchange_example_pdf(self):
        if len(self.example_pdf)>1 :
            to_keep_id = self.example_pdf[0].id
            self.example_pdf=(6,_,to_keep_id)
            raise UserError(_("Sorry, only 1 attachment is allowed. Remove current attachment first before adding a new one.")) 
            return
        if self.example_pdf :
            data = b64decode(self.example_pdf.datas)
            fd, pdf_file = tempfile.mkstemp(suffix="pdf")
            os.write(fd, data)
            os.close(fd)
            process = Popen(['pdftotext', '-enc', 'UTF-8', '-nopgbrk', '-layout', pdf_file, '-'], shell=False, stdout=PIPE)
            stdout, stderr = process.communicate()
            self.parsed_pdf = stdout
            if len(self.parsed_pdf)==0:
                self.parsed_pdf = "Something went wrong,.."+stdout
        else :
            self.parsed_pdf = "" 
        self.onchange_keyword()
        self.onchange_amount()
        self.onchange_amount_untaxed()
        self.onchange_date()
        self.onchange_invoice_number()
        self.onchange_description()
        return

    def onchange_searchfield(self, key):
        if not self.parsed_pdf or not key:
            result = ""
            return
        if key.find('(') == -1 or key.find(')') == -1 or key.find('(')>key.find(')') :
            return "brackets? '(..)'"
        match = re.search(key, self.parsed_pdf)
        if match :
            return match.group(1)
        else :
            return "no match"

    @api.multi
    @api.onchange('keyword')
    def onchange_keyword(self):
        if not self.keyword :
            self.keyword_result = ""
            return
        keyword = self.keyword
        if keyword.startswith('(') and keyword.endswith(')') :
            keyword = re.search("'(.*)")  #strip bounding quotes
        self.keyword_result = self.onchange_searchfield('('+keyword+')')
        return

    @api.multi
    @api.onchange('amount')
    def onchange_amount(self):
        self.amount_result = self.onchange_searchfield(self.amount)
        return

    @api.multi
    @api.onchange('amount_untaxed')
    def onchange_amount_untaxed(self):
        self.amount_untaxed_result = self.onchange_searchfield(self.amount_untaxed)
        return

    @api.multi
    @api.onchange('date')
    def onchange_date(self):
        self.date_result = self.onchange_searchfield(self.date)
        return

    @api.multi
    @api.onchange('invoice_number')
    def onchange_invoice_number(self):
        self.invoice_number_result = self.onchange_searchfield(self.invoice_number)
        return

    @api.multi
    @api.onchange('description')
    def onchange_description(self):
        self.description_result = self.onchange_searchfield(self.description)
        return

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
        if self.amount : 
            self.amount = self.convert2regex(self.amount)
            self.onchange_amount()
        else :
            self.amount_result = ""
        return

    @api.multi
    def amount_untaxed2regex(self):
        if self.amount_untaxed :
            self.amount_untaxed = self.convert2regex(self.amount_untaxed)
            self.onchange_amount_untaxed()
        else :
            self.amount_untaxed_result = ""
        return

    @api.multi
    def date2regex(self):
        if self.date :
            self.date = self.convert2regex(self.date)
            self.onchange_date()
        else :
            self.date_result = ""
        return

    @api.multi
    def invoice_number2regex(self):
        if self.invoice_number :
            self.invoice_number = self.convert2regex(self.invoice_number)
            self.onchange_invoice_number()
        else :
            self.invoice_number_result = ""
        return

    @api.multi
    def description2regex(self):
        if self.description :
            self.description = self.convert2regex(self.description)
            self.onchange_description()
        else :
            self.description_result = ""
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
            if tmpl.state == 'saved':
                tmpl.action_delete()
        super(I2dYmlTemplate, self).unlink()

    @api.model
    def create(self, values):
        res_id = super(I2dYmlTemplate, self).create(values)
        res_id.onchange_example_pdf() #recompute readonly values
        return res_id


class YmlTemplatePartner(models.Model):
    _name = "yml.template.partner"

    template_id = fields.Many2one('i2d.yml.template', string='Template')
    partner_id = fields.Many2one('res.partner', string='Vendor',
                                 domain=[('supplier', '=', True), ('is_company', '=', True)])
    partner_vat = fields.Char(related='partner_id.vat', string='VAT of Vendor')
    invoice_import_ids = fields.One2many('account.invoice.import.config',
                                        related='partner_id.invoice_import_ids', )
    company_id = fields.Many2one('res.company', related='partner_id.company_id', string='Partner Company')
