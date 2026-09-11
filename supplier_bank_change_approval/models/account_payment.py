from odoo import models, api


class AccountPayment(models.Model):

    # A bank account can only be used on a payment once it is confirmed

    _inherit = 'account.payment'

    @api.depends('partner_id', 'company_id', 'payment_type')
    def _compute_available_partner_bank_ids(self):
        # Drives both the domain of partner_bank_id and its default value.
        super()._compute_available_partner_bank_ids()
        for pay in self:
            pay.available_partner_bank_ids = pay.available_partner_bank_ids.filtered(
                lambda bank: bank.state == 'confirmed'
            )

    @api.constrains('partner_bank_id')
    def _check_partner_bank_id(self):
        self.partner_bank_id._check_approved()


class AccountPaymentRegister(models.TransientModel):

    _inherit = 'account.payment.register'

    def _get_batch_available_partner_banks(self, batch_result, journal):
        banks = super()._get_batch_available_partner_banks(batch_result, journal)
        return banks.filtered(lambda bank: bank.state == 'confirmed')
