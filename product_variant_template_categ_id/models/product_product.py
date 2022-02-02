# -*- coding: utf-8 -*-
# Copyright 2107 Alex Comba - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductProduct(models.Model):

    _inherit = 'product.product'

    categ_id = fields.Many2one(
        'product.category', 'Internal Category',
        change_default=True, domain="[('type','=','normal')]",
        required=True, help="Select category for the current product")

    @api.model
    def create(self, vals):
        product = super(ProductProduct, self).create(vals)
        template_vals = {}
        if 'categ_id' not in vals:
            template_vals['categ_id'] = product.product_tmpl_id.categ_id.id
        if template_vals:
            product.write(template_vals)
        return product
