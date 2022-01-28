# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AgedPartnerBalanceReport(models.TransientModel):

    _inherit = 'report_aged_partner_balance'

    operating_unit_id = fields.Many2one(comodel_name='operating.unit')

class AgedPartnerBalanceReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_aged_partner_balance'

    def _prepare_report_open_items(self):
        res = super(AgedPartnerBalanceReportCompute, self)._prepare_report_open_items()
        res['operating_unit_id'] = self.operating_unit_id and self.operating_unit_id.id or False
        return res
