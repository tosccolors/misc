# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid))