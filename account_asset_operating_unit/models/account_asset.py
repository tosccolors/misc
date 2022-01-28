# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero
from odoo.exceptions import UserError, ValidationError

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid))

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id.linked_operating_unit:
            self.operating_unit_id = self.analytic_account_id.operating_unit_ids.ids[0]
        else:
            self.operating_unit_id = False

class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        prec = self.env['decimal.precision'].precision_get('Account')
        for line in self:
            if line.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry! Please post or delete it.'))
            category_id = line.asset_id.category_id
            operating_unit_id = line.asset_id.operating_unit_id.id or False
            analytic_account_id = line.asset_id.analytic_account_id.id or False
            depreciation_date = self.env.context.get(
                'depreciation_date') or line.depreciation_date or fields.Date.context_today(self)
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount = current_currency.with_context(date=depreciation_date).compute(line.amount, company_currency)
            asset_name = line.asset_id.name + ' (%s/%s)' % (line.sequence, len(line.asset_id.depreciation_line_ids))
            move_line_1 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                # 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
                'analytic_account_id': analytic_account_id,
                'operating_unit_id': operating_unit_id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and - 1.0 * line.amount or 0.0,
            }
            move_line_2 = {
                'name': asset_name,
                'account_id': category_id.account_depreciation_expense_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': category_id.journal_id.id,
                'partner_id': line.asset_id.partner_id.id,
                # 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
                'analytic_account_id': analytic_account_id,
                'operating_unit_id': operating_unit_id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and line.amount or 0.0,
            }
            move_vals = {
                'ref': line.asset_id.code,
                'date': depreciation_date or False,
                'journal_id': category_id.journal_id.id,
                'operating_unit_id': operating_unit_id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            }
            move = self.env['account.move'].create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves.filtered(
                lambda m: any(m.asset_depreciation_ids.mapped('asset_id.category_id.open_asset'))).post()
        return [x.id for x in created_moves]

    @api.multi
    def create_grouped_move(self, post_move=True):
        if not self.exists():
            return []

        created_moves = self.env['account.move']
        category_id = self[0].asset_id.category_id  # we can suppose that all lines have the same category
        depreciation_date = self.env.context.get('depreciation_date') or fields.Date.context_today(self)
        operating_unit_id = self[0].asset_id.operating_unit_id.id or False
        analytic_account_id = self[0].asset_id.analytic_account_id.id or False
        amount = 0.0
        for line in self:
            # Sum amount of all depreciation lines
            company_currency = line.asset_id.company_id.currency_id
            current_currency = line.asset_id.currency_id
            amount += current_currency.compute(line.amount, company_currency)

        name = category_id.name + _(' (grouped)')
        move_line_1 = {
            'name': name,
            'account_id': category_id.account_depreciation_id.id,
            'debit': 0.0,
            'credit': amount,
            'journal_id': category_id.journal_id.id,
            # 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'sale' else False,
            'analytic_account_id': analytic_account_id,
            'operating_unit_id': operating_unit_id,
        }
        move_line_2 = {
            'name': name,
            'account_id': category_id.account_depreciation_expense_id.id,
            'credit': 0.0,
            'debit': amount,
            'journal_id': category_id.journal_id.id,
            # 'analytic_account_id': category_id.account_analytic_id.id if category_id.type == 'purchase' else False,
            'analytic_account_id': analytic_account_id,
            'operating_unit_id': operating_unit_id,
        }
        move_vals = {
            'ref': category_id.name,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'operating_unit_id': operating_unit_id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        move = self.env['account.move'].create(move_vals)
        self.write({'move_id': move.id, 'move_check': True})
        created_moves |= move

        if post_move and created_moves:
            self.post_lines_and_close_asset()
            created_moves.post()
        return [x.id for x in created_moves]
