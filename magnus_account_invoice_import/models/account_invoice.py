# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    source_email = fields.Char()

    @api.multi
    def action_create_source_email_partner(self):
        partners = self.env['res.partner']
        for this in self:
            if not this.source_email:
                continue
            if this.source_email in (
                    this.partner_id + this.partner_id.child_ids
            ).mapped('email'):
                continue
            partners += self.env['res.partner'].create({
                'type': 'invoice',
                'name': this.partner_id.name,
                'email': this.source_email,
                'parent_id': this.partner_id.commercial_partner_id.id,
            })
            this.source_email = False
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'domain': [('id', 'in', partners.ids)],
            'view_type': 'form',
            'view_mode': 'tree,form',
        }
