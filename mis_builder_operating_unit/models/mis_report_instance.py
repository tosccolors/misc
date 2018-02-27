# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class MisReportInstancePeriod(models.Model):
    _inherit = 'mis.report.instance.period'

    @api.multi
    def _get_additional_move_line_filter(self):
        self.ensure_one()
        res = super(MisReportInstancePeriod, self)._get_additional_move_line_filter()
        operating_unit_ids = self.report_instance_id.operating_unit_ids.ids
        if operating_unit_ids:
            res.append(('operating_unit_id', 'in', operating_unit_ids))
        return res


class MisReportInstance(models.Model):
    _inherit = 'mis.report.instance'

    operating_unit_ids = fields.Many2many('operating.unit', string='Operating Units', default=lambda self: self.env['res.users']._get_operating_units())

    @api.onchange('company_id', 'multi_company', 'company_ids')
    def onchange_company(self):
        res = {}
        res['domain'] = {}
        company_ids = []
        if self.company_id:
            company_ids.append(self.company_id.id)
        if self.multi_company and self.company_ids:
            company_ids =  self.company_ids.ids
        self.operating_unit_ids = (self.operating_unit_ids.filtered(lambda op: (op.company_id.id in company_ids)))
        if company_ids:
            res['domain'] = {'operating_unit_ids': [('company_id','in', company_ids)]}
        return res