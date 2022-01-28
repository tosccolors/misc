# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TrialBalanceReport(models.TransientModel):


    _inherit = 'report_trial_balance'

    operating_unit_id = fields.Many2one(comodel_name='operating.unit')

class TrialBalanceReportCompute(models.TransientModel):

    _inherit = 'report_trial_balance'

    def _prepare_report_general_ledger(self, account_ids):
        res = super(TrialBalanceReportCompute, self)._prepare_report_general_ledger(account_ids)
        res['operating_unit_id'] = self.operating_unit_id and self.operating_unit_id.id or False
        return res

