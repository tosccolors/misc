from odoo import models, api


class AccountPaymentOrder(models.Model):

    # A payment order may only contain confirmed bank accounts

    _inherit = 'account.payment.order'

    def _check_partner_banks_approved(self):
        self.payment_line_ids.partner_bank_id._check_approved()

    def draft2open(self):
        self._check_partner_banks_approved()
        return super().draft2open()

    def open2generated(self):
        # The bank account may have been changed (and thus reset to draft)
        # after the order was confirmed; re-check before generating the file.
        self._check_partner_banks_approved()
        return super().open2generated()


class AccountPaymentLine(models.Model):

    _inherit = 'account.payment.line'

    @api.onchange('partner_id')
    def partner_id_change(self):
        super().partner_id_change()
        if self.partner_bank_id and self.partner_bank_id.state != 'confirmed':
            self.partner_bank_id = self.partner_id.bank_ids.filtered(
                lambda bank: bank.state == 'confirmed'
            )[:1]

    @api.constrains('partner_bank_id')
    def _check_partner_bank_id(self):
        self.partner_bank_id._check_approved()


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def _prepare_payment_line_vals(self, payment_order):
        vals = super()._prepare_payment_line_vals(payment_order)
        # When the journal item carries no bank account, core falls back to the
        # partner's first bank account, which may still be awaiting approval.
        # Fall back to the first confirmed one instead; an unapproved account
        # explicitly set on the journal item is left as is and rejected by the
        # payment line constraint.
        if not self.partner_bank_id and vals.get('partner_bank_id'):
            bank = self.env['res.partner.bank'].browse(vals['partner_bank_id'])
            if bank.state != 'confirmed':
                vals['partner_bank_id'] = self.partner_id.bank_ids.filtered(
                    lambda b: b.state == 'confirmed'
                )[:1].id
        return vals
