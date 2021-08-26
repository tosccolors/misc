# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        result = super(SaleOrderLine, self).product_id_change()
        result['domain']['tax_id'] = [('type_tax_use', '=', 'sale'),
                                      ('company_id', '=', self.order_id.company_id.id)]
        if not self.product_id \
            and self.order_id.fiscal_position_id.country_tax:
            result['domain']['tax_id'] += [('country_id', '=', self.order_id.partner_id.country_id.id)]

        return result
