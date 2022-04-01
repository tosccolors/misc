# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Attachment(models.Model):
    _inherit = 'ir.attachment'

    @api.depends('res_model', 'res_id')
    @api.multi
    def _compute_source_ref(self):
        for line in self:
            line.source_res_model = ''
            line.source_res_id = ''
            if line.res_model == 'account.invoice' and line.res_id:
                inv = self.env[line.res_model].browse(line.res_id)
                if inv and inv.move_id:
                    line.source_res_model = 'account.move'
                    line.source_res_id = inv.move_id and inv.move_id.id or ''

    source_res_model = fields.Char('Source Res Model',compute='_compute_source_ref', store=True)
    source_res_id = fields.Char('Source Res ID',compute='_compute_source_ref', store=True,)