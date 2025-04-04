# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Purchase(models.Model):
    _inherit = 'purchase.order'


    def button_confirm(self):
        if self.date_planned and self.date_planned.date() <= fields.Datetime.now().date():
            raise ValidationError(
                _("Excepted/Planned date must be future date!")
            )
        res = super().button_confirm()
        for pick in self.picking_ids:
            pick.transfer_picking_to_monta()
        return res


    def write(self, vals):
        res = super().write(vals)

        for record in self:
            # Exclusive for updating Monta Shipment date
            if 'date_planned' in vals:
                for pick in self.picking_ids:
                    pick.scheduled_date = vals['date_planned']
        return res
