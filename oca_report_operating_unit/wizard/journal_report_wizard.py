# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class JournalReportWizard(models.TransientModel):
    _inherit = 'journal.ledger.report.wizard'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit'
    )

    @api.multi
    def _prepare_report_journal(self):
        res = super(JournalReportWizard, self)._prepare_report_journal()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res