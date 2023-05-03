
from odoo import api, fields, models, _


class StockLocation(models.Model):
    _inherit = "stock.location"

    level = fields.Integer(compute='_compute_level', store=True)

    @api.depends('location_id')
    def _compute_level(self):
        for location in self:
            level = 1
            parent = location.location_id
            while parent:
                level += 1
                parent = parent.location_id
            location.level = level
