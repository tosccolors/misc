# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.onchange('product_id')
    def product_id_onchange(self):
        data = {'invoice_line_tax_ids': [('company_id', '=', self.invoice_id.company_id.id)]}
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            type_tax_use = 'purchase'
        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            type_tax_use = 'sale'
            if not self.product_id \
                    and self.invoice_id.fiscal_position_id.country_tax:
                data['invoice_line_tax_ids'] += [('country_id', '=', self.invoice_id.partner_id.country_id.id)]
        data['invoice_line_tax_ids'] += [('type_tax_use', '=', type_tax_use)]
        return {'domain': data}

    # @api.onchange('product_id')
    # def _onchange_product_id(self):
    #     result = super(AccountInvoiceLine(), self)._onchange_product_id()
    #     if not self.product_id \
    #             and self.invoice_id.fiscal_position_id.country_tax \
    #             and type not in ('in_invoice', 'in_refund'):
    #         result['domain']['invoice_line_tax_ids'] = [('country_id','=',self.invoice_id.partner_id.country_id.id)]
    #     return result

    # @api.onchange('account_id')
    # def _onchange_account_id(self):
    #     if not self.account_id:
    #         return
    #     if not self.product_id:
    #         fpos = self.invoice_id.fiscal_position_id
    #         self.invoice_line_tax_ids = fpos.map_tax(self.account_id.tax_ids, partner=self.partner_id).ids
    #     elif not self.price_unit:
    #         self._set_taxes()