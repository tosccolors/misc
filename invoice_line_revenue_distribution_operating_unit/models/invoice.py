# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.model
    def invoice_line_move_line_get(self):
        """Copy operating_unit_id from invoice line to move lines"""
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        ailo = self.env['account.invoice.line']
        for move_line_dict in res:
            iline = ailo.browse(move_line_dict['invl_id'])
            move_line_dict['operating_unit_id'] = iline.operating_unit_id.id
        return res

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
#        import pdb; pdb.set_trace()
#        old_move_lines = move_lines
#        move_lines = super(AccountInvoice, self).finalize_invoice_move_lines(move_lines)
        new_move_lines = []
        for line_tuple in move_lines:
            if not line_tuple[2]['operating_unit_id']:
                line_tuple[2]['operating_unit_id'] = \
                    self.operating_unit_id.id
            new_move_lines.append(line_tuple)
        return new_move_lines

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res['operating_unit_id'] = line.get('operating_unit_id', False)
        return res

    def inv_line_characteristic_hashcode(self, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        res = super(AccountInvoice, self).inv_line_characteristic_hashcode(invoice_line)
        return res + "%s" % (
            invoice_line['operating_unit_id']
        )


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"


    @api.depends('account_analytic_id', 'invoice_id.operating_unit_id')
    @api.multi
    def _compute_operating_unit(self):
        for line in self:
            if line.account_analytic_id \
                    and line.account_analytic_id.linked_operating_unit:
                line.operating_unit_id = \
                    line.account_analytic_id.operating_unit_ids.id
            else:
                line.operating_unit_id = line.invoice_id.operating_unit_id

    operating_unit_id = fields.Many2one('operating.unit', related=False,
                                        compute='_compute_operating_unit',
                                        string='Operating Unit', store=True,
                                        readonly=True)
