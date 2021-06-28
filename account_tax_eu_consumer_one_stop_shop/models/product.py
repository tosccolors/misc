# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError



class ProductTemplate(models.Model):
    _inherit = "product.template"

    eu_consumer_country_tax_ids = fields.One2many(
        'eu.consumer.country.tax',
        'product_template_id',
        string='EU Consumer Tax per country'
     )


class EuConsumerCountryTax(models.Model):
    _name = 'eu.consumer.country.tax'

    product_template_id = fields.Many2one(
        'product.template',
        string="Product"
    )
    country_id = fields.Many2one(
        'res.country',
        string="EU Country",
        domain=[('intrastat', '=', True)]
    )
    tax_id = fields.Many2one(
        'account.tax',
        string="Tax for this Country",
    )