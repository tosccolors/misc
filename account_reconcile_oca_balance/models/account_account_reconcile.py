from odoo import api, fields, models


class AccountAccountReconcile(models.Model):
    _inherit = 'account.account.reconcile'

    balance = fields.Monetary(compute='_compute_balance')

    @api.depends('reconcile_data_info')
    def _compute_balance(self):
        for this in self:
            this.balance = sum([
                move_data.get('amount', 0)
                for move_data in this.reconcile_data_info['data']
            ])
