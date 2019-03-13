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

    @api.onchange('analytic_account_id')
    @api.multi
    def onchange_operating_unit(self):
            if self.analytic_account_id and self.analytic_account_id.linked_operating_unit:
                self.operating_unit_id = self.analytic_account_id.operating_unit_ids.id


    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        store=True
    )


    @api.multi
    @api.constrains('operating_unit_id', 'analytic_account_id')
    def _check_analytic_operating_unit(self):
        for rec in self:
            if (rec.analytic_account_id
                and rec.analytic_account_id.linked_operating_unit
                and rec.operating_unit_id
                and not rec.operating_unit_id.id == rec.analytic_account_id.operating_unit_ids.id):
                    raise UserError(_('The Operating Unit in the'
                                  ' Move Line must be the defined linked'
                                  'Operating Unit in the Analytic Account'))
            if (rec.operating_unit_id
                and rec.analytic_account_id
                and not rec.analytic_account_id.linked_operating_unit
                and not len(rec.analytic_account_id.operating_unit_ids) == 0
                and not rec.operating_unit_id in rec.analytic_account_id.operating_unit_ids):
                    raise UserError(_('The Operating Unit in the'
                                  ' Move Line must be in the defined '
                                  'Operating Units in the Analytic Account'
                                  ' or no OU\'s must be defined .'))

class AccountMove(models.Model):
    _inherit = "account.move"

    #override post(), when first post, nothing extra. When move.name exists, it cannot be first posting. Then 'OU-balancing' lines are unlinked.
    @api.multi
    def post(self):
        for move in self:
            if not move.company_id.ou_is_self_balanced or not move.name:
                continue
            for line in move.line_ids:
                if line.name == 'OU-Balancing':
                    line.with_context(wip=True).unlink()
        res = super(AccountMove, self).post()
        return res


