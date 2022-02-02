# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import models, fields, api, _
from odoo import tools
from odoo.exceptions import ValidationError, UserError
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
    user_id = fields.Many2one(
        'res.users',
        string='User Invoice Import',
        required=False,
        translate=False,
        readonly=False
        )

    @api.multi
    @api.constrains('user_id')
    def _check_company(self):
        for task in self:
            if task.company_id and task.user_id and not task.company_id == task.user_id.company_id:
                raise UserError(_('Configuration error!\nThe company\
                        must be the same as the company of the user in the task.'))

    @api.multi
    def _prepare_attachment_vals(self, datas, filename, md5_datas):
        vals = super(Task, self)._prepare_attachment_vals(datas=datas, filename=filename, md5_datas=md5_datas)
        vals_add = {}
        if self.location_id == self.env.ref('batch_vendor_invoice_import_new.batch_invoice_import_location'):
            vals_add = {
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
        vals.update(vals_add)
        return vals