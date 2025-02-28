# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        operating_unit_id = self.env.context.get('default_operating_unit_id')
        operating_unit = self.env['operating.unit'].browse(operating_unit_id or [])
        
        def search_read(*args, **kwargs):
            return [{'id': operating_unit.company_id.id}]

        try:
            if operating_unit:
                self.env["res.company"]._patch_method('search_read', search_read)
                self = self.with_context(default_operating_unit_id=operating_unit.id)
            return super().message_new(msg_dict, custom_values=custom_values)
        finally:
            if operating_unit:
                self.env["res.company"]._revert_method('search_read')
