# -*- coding: utf-8 -*-
# Author: Damien Crier, Andrea Stirpe, Kevin Graveman, Dennis Sluijk
# Author: Julien Coux
# Copyright 2016 Camptocamp SA, Onestein B.V.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class AgedPartnerBalance(models.TransientModel):
    """Aged partner balance report wizard."""

    _inherit = 'aged.partner.balance.wizard'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit'
    )

    def _prepare_report_aged_partner_balance(self):
        res = super(AgedPartnerBalance, self)._prepare_report_aged_partner_balance()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res
    #
    # def _export(self, report_type):
    #     """Default export is PDF."""
    #     model = self.env['report_aged_partner_balance_qweb']
    #     report = model.create(self._prepare_report_aged_partner_balance())
    #     report.compute_data_for_report()
    #     return report.print_report(report_type)
