from odoo import models, fields, api
from odoo.tools.translate import _

class AccountMoveReversal(models.TransientModel):
    """
    Account move reversal wizard, it cancel an account move by reversing it.
    """
    _inherit = 'account.move.reversal'

    
    def reverse_moves(self):
        ac_move_ids = self._context.get('active_ids', False)
        company = self.env.user.company_id
        via_sql_jq = company.reversal_via_sql or company.perform_reversal_by_line_jq \
                     or company.reversal_via_jq
        res = []
        if not via_sql_jq:
            res = self.env['account.move'].browse(ac_move_ids).reverse_moves(self.date, self.journal_id or False)

        else:
            moves = self.env['account.move']
            for wizard in self:
                orig = moves.browse(ac_move_ids)
                res += orig.create_reversals_via_job_sql(date=wizard.date, journal=wizard.journal_id or False)
        if res:
            return {
                'name': _('Reverse Moves'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.move',
                'domain': [('id', 'in', res)],
            }
        return {'type': 'ir.actions.act_window_close'}
