from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_payments_widget_to_reconcile_info(self):
        super()._compute_payments_widget_to_reconcile_info()
        for this in self:
            if not this.invoice_outstanding_credits_debits_widget:
                continue
            for line_vals in this.invoice_outstanding_credits_debits_widget['content']:
                line = self.env['account.move.line'].browse(line_vals['id'])
                if line_vals['journal_name'] != line.move_id.name:
                    line_vals['journal_name'] += ' (%s)' % line.move_id.name
