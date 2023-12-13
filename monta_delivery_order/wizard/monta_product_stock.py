# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import json

class MontaProductStock(models.TransientModel):
    _name = 'monta.product.stock'
    _description = 'Monta Stock'
    _rec_name = 'sku'

    sku = fields.Char("SKU")
    stock_inbound_forecasted = fields.Float('Stock Inbound Forecasted')
    stock_quarantaine = fields.Float('Stock Quarantaine')
    stock_all = fields.Float('Stock All')
    stock_blocked = fields.Float('Stock Blocked')
    stock_in_transit = fields.Float('Stock In Transit')
    stock_reserved = fields.Float('Stock Reserved')
    stock_available = fields.Float('Stock available')
    stock_whole_saler = fields.Float('Stock Whole Saler')
    stock_open = fields.Float('Stock Open')

    def action_fetch_stock(self):
        method="products"
        response = self.env['picking.from.odooto.monta'].call_monta_interface("GET", method)
        vals = []
        if response and response.status_code == 200:
            for data in json.loads(response.text)['Products']:
                product = data['Product']
                stock = data['Product']['Stock']
                prod_dt = {
                    'sku':product['Sku'],
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
                vals.append(prod_dt)
        self.search([]).unlink() #remove null records created when monta_get_product_stock_action() called
        self.create(vals)

        view_id = self.env.ref('monta_delivery_order.monta_product_stock_tree').id
        return {'type': 'ir.actions.act_window',
                'name': _('Monta Products Stock'),
                'res_model': 'monta.product.stock',
                'target': 'current',
                'view_mode': 'form',
                'views': [[view_id, 'tree']],
                }


    @api.model
    def monta_get_product_stock_action(self):
        """ Called by the button to get monta product stock."""
        view_id = self.env.ref('monta_delivery_order.monta_get_product_stock_form').id
        return {'type': 'ir.actions.act_window',
                'name': _('Get Monta Products Stock'),
                'res_model': 'monta.product.stock',
                'target': 'new',
                'view_mode': 'form',
                'views': [[view_id, 'form']],
                }
