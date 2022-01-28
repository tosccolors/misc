# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrialBalanceReportWizard(models.TransientModel):
    """Trial balance report wizard."""

    _inherit = "trial.balance.report.wizard"

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit'
    )

    def _prepare_report_trial_balance(self):
        res = super(TrialBalanceReportWizard, self)._prepare_report_trial_balance()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res

    def _export(self, report_type):
        """Default export is PDF."""
        model = self.env['report_trial_balance_qweb']
        report = model.create(self._prepare_report_trial_balance())
        report.compute_data_for_report()
        return report.print_report(report_type)
