from odoo import api, fields, models


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    def button_fully_paid_suspense(self, manual_reference, reconcile_data_info):
        self.ensure_one()
        reconcile_auxiliary_id = reconcile_data_info["reconcile_auxiliary_id"]
        self.reconcile_data_info = dict(reconcile_data_info, manual_reference=manual_reference)
        self.button_manual_reference_full_paid()
        return self._recompute_suspense_line(
                [
                    line for line in
                    self.reconcile_data_info.get("data", [])
                    if line['reference'] != "reconcile_auxiliary;%s" % reconcile_auxiliary_id
                ],
                self.reconcile_data_info['reconcile_auxiliary_id'],
                False,
        )
