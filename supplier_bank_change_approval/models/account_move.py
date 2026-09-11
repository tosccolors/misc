from odoo import models, api


class AccountMove(models.Model):

    # A bank account can only be used on an invoice once it is confirmed

    _inherit = 'account.move'

    @api.depends('bank_partner_id')
    def _compute_partner_bank_id(self):
        # Core picks the first bank account of the partner; never default to
        # one that is still awaiting approval.
        super()._compute_partner_bank_id()
        for move in self:
            if move.partner_bank_id and move.partner_bank_id.state != 'confirmed':
                move.partner_bank_id = move.bank_partner_id.bank_ids.filtered(
                    lambda bank: bank.state == 'confirmed'
                    and bank.company_id.id in (False, move.company_id.id)
                )[:1]

    @api.constrains('partner_bank_id')
    def _check_partner_bank_id(self):
        self.partner_bank_id._check_approved()
