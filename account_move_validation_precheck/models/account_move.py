from odoo import models, api
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    @api.multi
    def request_validation(self):
        for record in self:
            # Check if 'check_total' matches the total of the invoice
            if record.check_total != record.amount_total:
                raise UserError("Check the total of the invoice")

            # Check if 'invoice_date' is set
            if not record.invoice_date:
                raise UserError("Set an invoice date")

            # Check if 'payment_mode_id' is set
            if not record.payment_mode_id:
                raise UserError("Set a payment method")

            # Copy 'ref' to 'payment_reference'
            record.payment_reference = record.ref

        # Proceed with the original `request_validation` method
        return super(AccountMove, self).request_validation()
