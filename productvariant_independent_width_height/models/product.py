# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class productTemplate(models.Model):
    _inherit = "product.template"

    @api.onchange('height', 'width')
    def onchange_height_width(self):
        product_variant_ids = self.env['product.product'].search([('product_tmpl_id', '=', self._origin.id)])
        for variant in product_variant_ids:
            variant.write({'height': self.height})
            variant.write({'width': self.width})

class ProductProduct(models.Model):
    _inherit = 'product.product'

    height = fields.Integer('Height', help="Height advertising format in mm", store=True)
    width = fields.Integer('Width', help="Width advertising format in mm", store=True   )
