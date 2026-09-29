from odoo import models, api


class AccountMove(models.Model):

    # A bank account can only be used on an invoice once it is approved

    _inherit = 'account.move'

    @api.depends('bank_partner_id')
    def _compute_partner_bank_id(self):
        # Core defaults to the first bank account of the partner; never propose
        # one that is still awaiting approval.
        super()._compute_partner_bank_id()
        for move in self:
            if move.partner_bank_id._unapproved():
                move.partner_bank_id = move.bank_partner_id.bank_ids.filtered(
                    lambda bank: bank._is_approved()
                    and bank.company_id.id in (False, move.company_id.id)
                )[:1]

    @api.constrains('partner_bank_id')
    def _check_partner_bank_approved(self):
        for move in self:
            move.partner_bank_id._check_approved()

    def _post(self, soft=True):
        # The account may have been approved when it was selected and sent back
        # to draft afterwards (any change to a supplier account resets it), so
        # the state has to be re-checked at posting time. This is also the net
        # that catches accounts set by imports or by other modules.
        for move in self:
            move.partner_bank_id._check_approved()
        return super()._post(soft=soft)
