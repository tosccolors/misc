# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid))


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    @api.multi
    def create_move(self, post_move=True):
        move_ids = super(AccountAssetDepreciationLine, self).create_move(
            post_move=post_move)
        for line in self:
            if line.move_id:
                operating_unit_id = line.asset_id.operating_unit_id.id or False
                analytic_account_id = line.asset_id.analytic_account_id.id or False
                line.move_id.write({'operating_unit_id': operating_unit_id})
                line.move_id.line_ids.write({'operating_unit_id': operating_unit_id, 'analytic_account_id': analytic_account_id})
        return move_ids

    @api.multi
    def create_grouped_move(self, post_move=True):
        move_ids = super(AccountAssetDepreciationLine, self).create_grouped_move(post_move=post_move)
        if self[0].move_id:
            operating_unit_id = self[0].asset_id.operating_unit_id.id or False
            analytic_account_id = self[0].asset_id.analytic_account_id.id or False
            self[0].move_id.write({'operating_unit_id': operating_unit_id})
            self[0].move_id.line_ids.write({'operating_unit_id': operating_unit_id, 'analytic_account_id': analytic_account_id})
        return move_ids