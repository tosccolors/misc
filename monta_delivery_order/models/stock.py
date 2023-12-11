# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Picking(models.Model):
    _inherit = 'stock.picking'

    monta_log_id = fields.Many2one('picking.from.odooto.monta', copy=False)
    response_code = fields.Integer(related="monta_log_id.monta_response_code", string='Response Code')
    response_message = fields.Text(related="monta_log_id.monta_response_message", string='Response Message')

    def transfer_picking_to_monta(self):
        monta_picking_obj = self.env['picking.from.odooto.monta']
        lines = []
        for move in self.move_ids:
            lines.append((0, 0 ,{'move_id':move.id}))

        monta_picking_id = monta_picking_obj.create(
            {'picking_id':self.id, 'status':'draft', 'monta_stock_move_ids': lines})
        self.write({'monta_log_id': monta_picking_id})
        
        if self.picking_type_code == 'outgoing' and self.sale_id:
            monta_picking_id.monta_good_receipt_content()

        if self.picking_type_code == 'incoming' and self.purchase_id:
            monta_picking_id.monta_inbound_forecast_content()
        return monta_picking_id


    def button_validate(self):
        res = super().button_validate()
        if self.picking_type_code == 'outgoing' and not self.monta_log_id and self.state not in ('draft','done', 'cancel'):
            self.transfer_picking_to_monta()
        return res

    def action_assign(self):
        res = super().action_assign()
        if self.picking_type_code == 'outgoing' and not self.monta_log_id and self.state not in (
        'draft', 'done', 'cancel'):
            self.transfer_picking_to_monta()
        return res

    def action_confirm(self):
        res = super().action_confirm()
        if self.picking_type_code == 'outgoing' and not self.monta_log_id:
            self.transfer_picking_to_monta()
        return res

