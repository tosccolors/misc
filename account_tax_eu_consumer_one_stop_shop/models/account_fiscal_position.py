# -*- coding: utf-8 -*-

from ast import literal_eval
from operator import itemgetter
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    no_vat = fields.Boolean(string='No VAT', help="Apply only if partner has no VAT number.")
    country_tax = fields.Boolean(string='Apply Country VAT', help="Get tax from product and EU-country.")

    @api.model     # noqa
    def map_tax(self, taxes, product=None, partner=None):
        if self.country_tax and product:
            country_id = partner.country_id or False
            if not country_id:
                raise ValidationError(
                    _('No Country defined in Partner and "country_tax" is True. Please correct'))
            eu_consumer_country_tax_id = product.eu_consumer_country_tax_ids.search([('country_id','=', country_id.id)])
            if len(eu_consumer_country_tax_id) == 1:
                result = eu_consumer_country_tax_id.tax_id
            else:
                raise ValidationError(
                    _('More than one Taxes defined for the same Country on this Product. Please correct'))
        else:
            result = super(AccountFiscalPosition, self).map_tax(taxes, product=product, partner=partner)
        return result


class AccountTax(models.Model):
    _inherit = 'account.tax'

    country_id = fields.Many2one(
        'res.country',
        string="EU Country",
        domain=[('intrastat', '=', True)]
    )