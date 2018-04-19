# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import models, fields, api
from odoo import tools
from odoo.exceptions import ValidationError
from unidecode import unidecode

class Task(models.Model):
    _inherit = 'external.file.task'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        translate=False,
        readonly=False
        )

    @api.multi
    def _prepare_attachment_vals(self, datas, filename, md5_datas):
        vals = super(Task, self)._prepare_attachment_vals(datas=datas, filename=filename, md5_datas=md5_datas)
        vals_add = {}
        if self.location_id == self.env.ref('batch_vendor_invoice_import.batch_invoice_import_export_location'):
            vals_add = {
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
        elif self.location_id == self.env.ref('batch_vendor_invoice_import.batch_invoice_import_location'):
            ## pairing with files sent to OCR
            name = unidecode(filename.replace('.pdf', ''))
            attach_ocr = self.env['ir.attachment.metadata'].search([('internal_hash', '=', name),
                        ('location_id', '=', self.env.ref('batch_vendor_invoice_import.batch_invoice_import_export_location').id)])
            if not len(attach_ocr) == 1:
                raise ValidationError(_(
                    "There has to be one and only one exported file relating to this Invoice: '%s',"
                    " either there are no files or more than one" % filename))
            vals_add = {
                'company_id': attach_ocr.company_id.id,
                'operating_unit_id': attach_ocr.operating_unit_id.id,
                'paired_id': attach_ocr.id,
#                'name': attach_ocr.filename,
#                'datas_fname': filename,
            }
        vals.update(vals_add)
        return vals