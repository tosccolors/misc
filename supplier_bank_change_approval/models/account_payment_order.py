from odoo import models, api


class AccountPaymentOrder(models.Model):

    # A payment order may only contain approved bank accounts

    _inherit = 'account.payment.order'

    def _check_partner_banks_approved(self):
        for order in self:
            order.payment_line_ids.partner_bank_id._check_approved()

    def draft2open(self):
        self._check_partner_banks_approved()
        return super().draft2open()

    def open2generated(self):
        # A supplier account may have been changed (and thus sent back to
        # draft) after the order was confirmed; re-check before generating the
        # payment file.
        self._check_partner_banks_approved()
        return super().open2generated()


class AccountPaymentLine(models.Model):

    _inherit = 'account.payment.line'

    @api.constrains('partner_bank_id')
    def _check_partner_bank_approved(self):
        for line in self:
            line.partner_bank_id._check_approved()

    @api.onchange('partner_id')
    def partner_id_change(self):
        res = super().partner_id_change()
        # Core proposes the partner's first bank account; prefer an approved one.
        if self.partner_bank_id and not self.partner_bank_id._is_approved():
            self.partner_bank_id = self.partner_id.bank_ids.filtered(
                lambda bank: bank._is_approved()
            )[:1]
        return res


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def _prepare_payment_line_vals(self, payment_order):
        vals = super()._prepare_payment_line_vals(payment_order)
        # When the journal item carries no bank account of its own, core falls
        # back to the partner's first bank account, which may still be awaiting
        # approval. Prefer the first approved one. An unapproved account that
        # was explicitly set on the journal item is deliberately left in place,
        # so the payment line constraint rejects it loudly instead of silently
        # creating a payment line without a bank account.
        if not self.partner_bank_id and vals.get('partner_bank_id'):
            bank = self.env['res.partner.bank'].browse(vals['partner_bank_id'])
            if not bank._is_approved():
                approved = self.partner_id.bank_ids.filtered(
                    lambda b: b._is_approved()
                )[:1]
                if approved:
                    vals['partner_bank_id'] = approved.id
        return vals
