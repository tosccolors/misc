# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"


    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        new_move_lines = []
        for line_tuple in move_lines:
            if self.operating_unit_id and not line_tuple[2]['operating_unit_id']:
                line_tuple[2]['operating_unit_id'] = \
                    self.operating_unit_id.id
            new_move_lines.append(line_tuple)
        return new_move_lines

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        p = 0
        for line in self.invoice_line_ids:
            if line.quantity == 0:
                continue
            res[p]['operating_unit_id'] = line.operating_unit_id.id
            p += 1
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res['operating_unit_id'] = line.get('operating_unit_id', False)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.depends('account_analytic_id', 'invoice_id.operating_unit_id')
    @api.multi
    def _compute_operating_unit(self):
        for line in self:
            if line.account_analytic_id and line.account_analytic_id.linked_operating_unit:
                line.operating_unit_id = line.account_analytic_id.operating_unit_ids.id
            else:
                line.operating_unit_id = line.invoice_id.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit', related=False,
                                        compute='_compute_operating_unit',
                                        string='Operating Unit', store=True,
                                        readonly=True)
