# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Invoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def write(self, vals):
        res = super(Invoice, self).write(vals)
        if vals.get('move_id', False):
            attachment = self.env['ir.attachment']
            attachment_ids = attachment.search([('res_model', '=', self._name), ('res_id', 'in', self.ids)])
            attachment_ids.write({'source_res_model':'account.move','source_res_id':vals.get('move_id', False)})
        return res