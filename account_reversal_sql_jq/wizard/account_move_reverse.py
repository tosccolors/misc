# -*- coding: utf-8 -*-
# Copyright 2011 Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2012-2013 Guewen Baconnier (Camptocamp)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class AccountMoveReverse(models.TransientModel):
    _inherit = "account.move.reverse"


    @api.multi
    def action_reverse(self): 
        company = self.env.user.company_id
        via_sql_jq = company.reversal_via_sql or company.perform_reversal_by_line_jq \
                     or company.reversal_via_jq
        if not via_sql_jq:
            return super(AccountMoveReverse, self).action_reverse()
        
        moves = self.env['account.move']
        for wizard in self:
            orig = moves.browse(self.env.context.get('active_ids'))
            moves |= orig.create_reversals_via_job_sql(
                date=wizard.date, journal=wizard.journal_id,
                move_prefix=wizard.move_prefix, line_prefix=wizard.line_prefix,
                reconcile=wizard.reconcile)
        action = {
            'name': _('Reverse moves'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'account.move',
            'context': {'search_default_to_be_reversed': 0},
        }
        if len(moves) == 1:
            action.update({
                'view_mode': 'form,tree',
                'res_id': moves.id,
            })
        else:
            action.update({
                'view_mode': 'tree,form',
                'domain': [('id', 'in', moves.ids)],
            })
        return action
