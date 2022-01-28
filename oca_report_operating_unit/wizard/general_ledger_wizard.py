# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GeneralLedgerReportWizard(models.TransientModel):
    """General ledger report wizard."""

    _inherit = "general.ledger.report.wizard"

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit'
    )

    def _prepare_report_general_ledger(self):
        res = super(GeneralLedgerReportWizard, self)._prepare_report_general_ledger()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res