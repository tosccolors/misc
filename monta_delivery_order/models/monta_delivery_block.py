# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, fields, models, api


class DeliveryBlock(models.Model):
    _name = 'monta.delivery.block'
    _description = 'Deliver Block'

    name = fields.Char('Delivery Block Message')