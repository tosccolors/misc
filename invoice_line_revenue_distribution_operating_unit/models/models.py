# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    linked_operating_unit = fields.Boolean('Linked Operating Unit')

    @api.multi
    @api.constrains('operating_unit_ids', 'linked_operating_unit')
    def _check_length_operating_units(self):
        for aa in self:
            if (
                    aa.linked_operating_unit and
                    len(aa.operating_unit_ids) != 1
            ):
                raise ValidationError(_('Fill in one and only one Operating Unit. '
                                        'move lines with this analytic account '
                                        'will also have the linked Operating Unit.'))
        return True


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
            res[p]['operating_unit_id'] = line.operating_unit_id.id
            p += 1
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        res['operating_unit_id'] = line.get('operating_unit_id', False)
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    operating_unit_id = fields.Many2one('operating.unit',
                                        compute='_compute_ou',
                                        string='Operating Unit', store=True,
                                        readonly=True)

    @api.depends('account_analytic_id', 'invoice_id.operating_unit_id')
    @api.multi
    def _compute_ou(self):
        for line in self:
            if line.account_analytic_id and line.account_analytic_id.linked_operating_unit:
                line.operating_unit_id = line.account_analytic_id.operating_unit_ids.id
            else:
                line.operating_unit_id = line.invoice_id.operating_unit_id



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('team_id', 'operating_unit_id')
    def _check_team_operating_unit(self):
        for rec in self:
            if (rec.team_id and rec.team_id.operating_unit_id and
                    rec.team_id.operating_unit_id != rec.operating_unit_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Operating Unit of the sales team '
                                        'must match with that of the '
                                        'quote/sales order'))

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_sales_order_operating_unit(self):
        '''for rec in self:
            orders = self.env['sale.order'].search(
                [('team_id', '=', rec.id), ('operating_unit_id', '!=',
                                            rec.operating_unit_id.id)])
            if orders:
                raise ValidationError(_('Sales orders already exist '
                                        'referencing this team in other '
                                        'operating units.'))'''
        pass
