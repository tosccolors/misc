# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2018 Magnus Group B.V.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends('account_analytic_id', 'operating_unit_id')
    @api.multi
    def _compute_operating_unit(self):
        for line in self:
            if line.account_analytic_id and line.account_analytic_id.linked_operating_unit:
                line.operating_unit_id = line.account_analytic_id.operating_unit_ids.id
            elif not line.operating_unit_id:
                line.operating_unit_id = self.env['res.users'].\
                                            operating_unit_default_get(self._uid)

    operating_unit_id = fields.Many2one('operating.unit', compute='_compute_operating_unit',
                                        string='Operating Unit', store=True)


    @api.multi
    @api.constrains('operating_unit_id', 'account_analytic_id')
    def _check_analytic_operating_unit(self):
        for rec in self:
            if (rec.account_analytic_id
                and not rec.account_analytic_id.linked_operating_unit
                and rec.operating_unit_id
                and not len(rec.account_analytic_id.operating_unit_ids) == 0
                and not rec.operating_unit_id in rec.account_analytic_id.operating_unit_ids):
                raise UserError(_('The Operating Unit in the'
                                  ' Move Line must be in the defined '
                                  'Operating Units in the Analytic Account'
                                  ' or no OU\'s must be defined .'))

