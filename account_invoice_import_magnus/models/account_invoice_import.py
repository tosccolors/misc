# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        last_invoice = self.env['account.invoice'].search([], order='id desc', limit=1)
        result = super(AccountInvoiceImport, self).message_new(
            msg_dict, custom_values=custom_values,
        )
        new_invoices = self.env['account.invoice'].search([('id', '>', last_invoice.id)])
        for invoice in new_invoice:
            invoice.message_post(subtype='mail.mt_comment', **msg_dict)
        return result

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config=False):
        vals, config = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(
            parsed_inv, import_config=import_config,
        )
        msg_dict = self.env.context.get('account_invoice_import_ml_msg_dict')
        if msg_dict:
            for operating_unit in self.env['operating.unit'].search([]):
                if operating_unit.invoice_import_email in msg_dict.get('to'):
                    vals['operating_unit_id'] = operating_unit.id
        return vals, config
