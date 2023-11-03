# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Purchase(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        res = super().button_confirm()
        for pick in self.picking_ids:
            pick.transfer_picking_to_monta()
        return res