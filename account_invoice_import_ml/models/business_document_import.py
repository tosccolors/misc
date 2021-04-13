# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class BusinessDocumentImport(models.AbstractModel):
    _inherit = 'business.document.import'

    @api.model
    def _hook_match_partner(
            self, partner_dict, chatter_msg, domain, partner_type_label
    ):
        return self.env['res.partner'].search(
            [('supplier_invoice_name', '=ilike', partner_dict['name'])],
            limit=1,
        ) or super(BusinessDocumentImport, self)._hook_match_partner(
            partner_dict, chatter_msg, domain, partner_type_label,
        )
