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
    eu_consumer_country_account_ids = fields.One2many(
        'eu.consumer.country.account',
        'product_template_id',
        string='EU Consumer Revenue Account per country'
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
        domain=[('country_id', '=', country_id)]
    )



class EuConsumerCountryAccount(models.Model):
    _name = 'eu.consumer.country.account'

    product_template_id = fields.Many2one(
        'product.template',
        string="Product"
    )
    country_id = fields.Many2one(
        'res.country',
        string="EU Country",
        domain=[('intrastat', '=', True)]
    )
    account_id = fields.Many2one(
        'account.account',
        string="Revenue account for this Country"
    )