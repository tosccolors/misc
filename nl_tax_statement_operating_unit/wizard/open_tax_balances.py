# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _

class OpenTaxBalances(models.TransientModel):
    _inherit = 'wizard.open.tax.balances'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.multi
    def open_taxes(self):
        vals = super(OpenTaxBalances, self).open_taxes()
        vals['context'].update({
            'operating_unit_id':self.operating_unit_id and self.operating_unit_id.id or False
        })
        return vals