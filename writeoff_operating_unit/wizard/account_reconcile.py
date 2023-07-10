from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMoveLineReconcileWriteoff(models.TransientModel):
    """
    It opens the write off wizard form, in that user can define the journal, account, analytic account for reconcile
    """
    _inherit = 'account.move.line.reconcile.writeoff'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.model
    def default_get(self, fields):
        res = super(AccountMoveLineReconcileWriteoff, self).default_get(fields)
        move_lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
        operating_unit_id = move_lines.mapped('operating_unit_id')
        if len(operating_unit_id) > 1:
            raise UserError(
                _('Entries must have same operating unit.')
            )
        if 'operating_unit_id' in fields:
            res.update({'operating_unit_id': operating_unit_id.id})
        return res

    
    def trans_rec_reconcile(self):
        context = dict(self._context or {})
        if self.operating_unit_id:
            context['write_off_operating_unit_id'] = self.operating_unit_id.id
        return super(AccountMoveLineReconcileWriteoff, self.with_context(context)).trans_rec_reconcile()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _create_writeoff(self, vals):
        context = dict(self._context or {})
        operating_unit_id = context.get('write_off_operating_unit_id', False)
        if operating_unit_id:
            vals['operating_unit_id'] = operating_unit_id
        return super(AccountMoveLine, self)._create_writeoff(vals)
