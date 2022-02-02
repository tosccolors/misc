# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class VatStatement(models.Model):
    _inherit = 'l10n.nl.vat.statement'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', default=lambda self: self.env['res.users'].operating_unit_default_get(self._uid))


    def _compute_lines(self, lines):
        '''
            Inherited to add operating unit
        '''
        ctx = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'target_move': self.target_move,
            'company_id': self.company_id.id,
        }
        if self.operating_unit_id:
            ctx.update({'operating_unit_id':self.operating_unit_id.id})
        tags_map = self._get_tags_map()
        domain = self._get_taxes_domain()
        taxes = self.env['account.tax'].with_context(ctx).search(domain)
        for tax in taxes:
            for tag in tax.tag_ids:
                tag_map = tags_map.get(tag.id)
                if tag_map:
                    column = tag_map[1]
                    code = tag_map[0]
                    if column == 'omzet':
                        lines[code][column] += tax.base_balance
                    else:
                        lines[code][column] += tax.balance