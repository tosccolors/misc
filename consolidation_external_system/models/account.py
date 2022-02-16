# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAccount(models.Model):
    _inherit = 'account.account'

    ext_account = fields.Char('Group Account', help="Account Reference Code of an External System")