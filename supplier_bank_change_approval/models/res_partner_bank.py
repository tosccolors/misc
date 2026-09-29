from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerBank(models.Model):

    # Update vendor bank account with states

    _inherit = 'res.partner.bank'

    state = fields.Selection([('draft', "Draft"), ('confirmed', "Confirmed")], default='draft', string='Status', copy=False, index=True, readonly=True, store=True)

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'confirmed'

    def _is_approved(self):
        """A bank account may be used only once approved.

        Only supplier bank accounts go through approval, so any other account
        (a customer's, or the company's own) is always usable."""
        self.ensure_one()
        return self.state == 'confirmed' or not self.partner_id.is_supplier

    def _unapproved(self):
        return self.filtered(lambda bank: not bank._is_approved())

    def _check_approved(self):
        """Raise if any of these bank accounts is still awaiting approval.

        Central check used by invoices, payments and payment orders."""
        unapproved = self._unapproved()
        if unapproved:
            raise ValidationError(_(
                'The following supplier bank account(s) have been added or changed and are '
                'not yet approved, so they cannot be used:\n%s\n\n'
                'A Bank Account Manager must approve them first '
                '(Sensitive Fields Approval / Bank Account Approval).'
            ) % '\n'.join(
                '- %s (%s)' % (bank.acc_number, bank.partner_id.display_name)
                for bank in unapproved
            ))

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id') or [])
        if partner.is_supplier:
            vals['state'] = 'draft'
        else:
            vals['state'] = 'confirmed'
        return super().create(vals)

    def write(self, vals):
        if any(self.mapped('partner_id.is_supplier')) and set(vals) != set(['state']):
            vals['state'] = 'draft'
        return super().write(vals)
