# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = ['product.product', 'data.track.thread']