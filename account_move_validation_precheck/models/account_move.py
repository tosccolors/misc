from odoo import models, api
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _precheck_validation(self):
        """Perform pre-validation checks before calling request_validation."""
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

    def request_validation(self):
        # Run pre-validation checks
        self._precheck_validation()

        # Proceed with the original request_validation logic
        return super(AccountMove, self).request_validation()
