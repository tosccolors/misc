# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MontaStockLot(models.Model):
    _name = 'monta.stock.lot'
    _order = 'create_date desc'
    _rec_name = 'batch_ref'
    _description = 'Monta Lot'

    batch_id = fields.Char('Batch ID')
    batch_ref = fields.Char(string='Title/Batch Ref')
    batch_quantity = fields.Float(string='Batch Quantity')
    monta_inbound_id = fields.Many2one('monta.inboundto.odoo.move')
    monta_outbound_id = fields.Many2one('stock.move.from.odooto.monta')
    monta_product_lot_id = fields.Many2one('monta.product.stock.lot')
    monta_create_date = fields.Datetime(string="Monta Creation Date")
    

class MontaProductStockLot(models.Model):
    _name ='monta.product.stock.lot'
    _order = 'create_date desc'
    _rec_name = 'sku'
    _description = 'Monta Product Lot'

    @api.depends('sku')
    def _compute_product_id(self):
        pro_obj = self.env['product.product']
        for pro in self:
            product = pro_obj.search([('default_code', '=', pro.sku)], limit=1)
            pro.product_id = product and product.id or pro_obj

    product_id = fields.Many2one('product.product', compute=_compute_product_id, store=True, string='Product')
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
    monta_stock_lot_ids = fields.One2many('monta.stock.lot', 'monta_product_lot_id', string="Monta Stock Lot")
    batches_count = fields.Integer(compute='_compute_batches_count')

    @api.depends('monta_stock_lot_ids')
    def _compute_batches_count(self):
        batches_data = self.env['monta.stock.lot']._read_group([('monta_product_lot_id', 'in', self.ids)], ['monta_product_lot_id'],
                                                                           ['monta_product_lot_id'])
        batch_count = {x['monta_product_lot_id'][0]: x['monta_product_lot_id_count'] for x in batches_data}
        for bt in self:
            bt.batches_count = batch_count.get(bt.id, 0)

    def map_odoo_product(self):
        self.ensure_one()
        if self.product_id:
            return
        pro_obj = self.env['product.product']
        product = pro_obj.search([('default_code', '=', self.sku)], limit=1)
        if not product:
            raise UserError(
                _("Product Not Found: Cannot do Inventory Adjustment for SKU %s") % self.sku
            )
        self.product_id = product.id

    def do_inventory_adjustment(self):
        stockQuant = adjustment_applied_quant = self.env['stock.quant']
        company_id = self.env.company.id
        for self_obj in self:
            self_obj.map_odoo_product()

            stockQuant._quant_tasks()

            product = self_obj.product_id
            for batch_obj in self_obj.monta_stock_lot_ids:
                # name = product.default_code+'_'+batch_obj.batch_ref
                name = batch_obj.batch_ref

                sQuant_obj = stockQuant.search([('product_id', '=', product.id),
                                                ('lot_id.name','=',name),
                                                ('location_id.usage', 'in',
                                                 ['internal', 'transit'])])
                if not sQuant_obj:
                    lot_dic= {
                        'company_id': company_id,
                        'name': name,
                        'product_id': product.id
                    }
                    lot_obj = self.env['stock.lot'].create(lot_dic)

                    location = self.env['stock.location']. \
                        search([('usage', 'in', ['internal', 'transit']),
                                ('company_id', '=', company_id), ('replenish_location', '=', True)], limit=1)
                    sQuant_obj = sQuant_obj.create(
                        {'product_id':product.id,
                         'lot_id':lot_obj.id,
                         'location_id':location.id
                         }
                    )

                if sQuant_obj.quantity != batch_obj.batch_quantity:
                    sQuant_obj.inventory_quantity = batch_obj.batch_quantity
                    adjustment_applied_quant |= sQuant_obj

        if adjustment_applied_quant:
            adjustment_applied_quant.action_apply_inventory()
