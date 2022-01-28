# -*- coding: utf-8 -*-
# Copyright 2018 Magnus ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    def asset_create(self):
        res = super(AccountInvoiceLine, self).asset_create()
        if self.asset_category_id:
            assets = self.env['account.asset.asset'].search([('code', '=', self.invoice_id.number), ('company_id', '=', self.company_id.id)])
            if assets:
                assets.write({'operating_unit_id': self.invoice_id.operating_unit_id.id or False})
        return res