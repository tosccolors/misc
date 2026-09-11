from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):

    # Update vendor bank account with states

    _inherit = 'res.partner.bank'

    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")], default='draft', string='Status', copy=False, index=True, readonly=True, store=True, track_visibility='always')

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def _check_approved(self):
        """Raise if any of these bank accounts is not yet approved.

        Central check used by invoices, payments and payment orders: a bank
        account may only be used once it has been confirmed by a Bank Account
        Manager."""
        unapproved = self.filtered(lambda bank: bank.state != 'confirmed')
        if unapproved:
            raise ValidationError(_(
                'The following bank account(s) have been added or changed and are not yet approved, '
                'so they cannot be used:\n%s'
            ) % '\n'.join(
                '- %s (%s)' % (bank.acc_number, bank.partner_id.display_name)
                for bank in unapproved
            ))

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id') or [])
        if partner.supplier_rank:
            vals['state'] = 'draft'
        else:
            vals['state'] = 'confirmed'
        return super().create(vals)

    def write(self, vals):
        if any(self.mapped('partner_id.supplier_rank')) and set(vals) != set(['state']):
            vals['state'] = 'draft'
        return super().write(vals)
