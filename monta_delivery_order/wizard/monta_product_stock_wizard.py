# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import json

class MontaProductStockWizard(models.TransientModel):
    _name = 'monta.product.stock.wizard'
    _description = 'Monta Stock Wizard'

    name = fields.Char('SKU(s)')
    is_sku = fields.Boolean('Fetch Stock Selected From Sku?')

    def action_fetch_stock(self):
        domain = [('default_code', '!=', False)]
        if self.is_sku:
            sku_list = ''.join(self.name.split()).split(',')
            domain = [('default_code', '=', sku_list)]
            if len(sku_list) > 1:
                domain = [('default_code', 'in', sku_list)]
        for template_dt in self.env['product.template'].sudo().search_read(domain, ['default_code']):
            method="product/"+template_dt['default_code']+'/stock'
            response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
            create_vals = []
            write_vals = {}
            if response and response.status_code == 200:
                data = json.loads(response.text)
                # product = data['Product']
                sku = data['Sku']
                stock = data['Stock']
                batches = data['Stock'].get('Batches', [])
                prod_dt = {
                    'sku':sku,
                    'stock_inbound_forecasted':stock['StockInboundForecasted'],
                    'stock_quarantaine':stock['StockQuarantaine'],
                    'stock_all':stock['StockAll'],
                    'stock_blocked':stock['StockBlocked'],
                    'stock_in_transit':stock['StockInTransit'],
                    'stock_reserved':stock['StockReserved'],
                    'stock_available':stock['StockAvailable'],
                    'stock_whole_saler':stock['StockWholeSaler'],
                    'stock_open':stock['StockOpen'],
                }
                batch_dt = []
                for batch in batches:
                    ref = batch['Reference']
                    qty = batch['Quantity']
                    batch_dt.append((0, 0, {'batch_ref':ref, 'batch_quantity': qty}))
                prod_dt['monta_stock_lot_ids'] = batch_dt
                lot = self.env['monta.product.stock.lot'].search([('sku', '=', sku)])
                if lot:
                    write_vals[lot] = prod_dt
                else:
                    create_vals.append(prod_dt)
            if create_vals:
                self.env['monta.product.stock.lot'].create(create_vals)
            for lot_obj, dt in write_vals.items():
                lot_obj.monta_stock_lot_ids.unlink()
                lot_obj.write(dt)

        return {'type': 'ir.actions.act_window',
                'name': _('Monta Products Stock'),
                'res_model': 'monta.product.stock.lot',
                'target': 'current',
                'view_mode': 'form',
                'views': [[False, 'tree'], [False, 'form']],
                }


    # @api.model
    # def monta_get_product_stock_action(self):
    #     """ Called by the button to get monta product stock."""
    #     view_id = self.env.ref('monta_delivery_order.monta_get_product_stock_form').id
    #     return {'type': 'ir.actions.act_window',
    #             'name': _('Get Monta Products Stock'),
    #             'res_model': 'monta.product.stock.wizard',
    #             'target': 'new',
    #             'view_mode': 'form',
    #             'views': [[view_id, 'form']],
    #             }
