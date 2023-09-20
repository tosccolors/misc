# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sent_date = fields.Date(string="Sent Date")
