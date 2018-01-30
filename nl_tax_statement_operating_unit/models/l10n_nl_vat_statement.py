# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class VatStatement(models.Model):
    _inherit = 'l10n.nl.vat.statement'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid))