from odoo import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)



class MontaSyncLog(models.Model):
    _name = 'monta.sync.log'
    _order = 'id desc'

    name = fields.Char("Monta Reference")
    type = fields.Selection([('outbound', 'Outbound Orders')], 'Type', default='outbound')
    state = fields.Selection([('ok', 'Sync Ok'), ('process', 'Processing'), ('error', 'Error')], 'Status')
    remarks = fields.Text("Remarks")
    sale_id = fields.Many2one("sale.order", 'Sale Order')
    picking_id = fields.Many2one("stock.picking", 'Delivery Order')