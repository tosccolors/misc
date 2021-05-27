# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models
from odoo.tools.mail import email_split


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"
    
    @api.model
    def message_new(self, msg_dict, custom_values=None):
        last_invoice = self.env['account.invoice'].search([], order='id desc', limit=1)
        result = super(AccountInvoiceImport, self).message_new(
            msg_dict, custom_values=custom_values,
        )
        new_invoices = self.env['account.invoice'].search([('id', '>', last_invoice.id)])
        for invoice in new_invoices:
            invoice.message_post(
                subtype='mail.mt_comment',
                **{
                    key: value for key, value in msg_dict.items()
                    if key != 'attachments'
                }
            )
        if not new_invoices:
            try:
                partner = self.env['business.document.import']._match_partner(
                    dict(email=msg_dict.get('email_from')), '',
                )
            except exceptions.UserError:
                partner = self.env.ref('account_invoice_import_ml.unknown_supplier')
            self.env['account.invoice'].message_new(
                msg_dict, custom_values=dict(partner_id=partner.id),
            )
        return result

    @api.model
    def _account_invoice_import_ml_add_email(self, partner, email, data):
        if '@magnus' in email:
            # suppress all vendor related actions if the mail came from a magnus employee
            return
        return super(AccountInvoiceImport, self)._account_invoice_import_ml_add_email(
            partner, email, data,
        )

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config=False):
        vals, config = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(
            parsed_inv, import_config=import_config,
        )
        msg_dict = self.env.context.get('account_invoice_import_ml_msg_dict')
        if msg_dict:
            emails = map(
                unicode.upper,
                email_split(
                    '%s,%s' % (msg_dict.get('to'), msg_dict.get('cc'))
                )
            )
            for operating_unit in self.env['operating.unit'].search([]):
                if not operating_unit.invoice_import_email:
                    continue
                for email in email_split(operating_unit.invoice_import_email):
                    if email.upper() in emails:
                        vals['operating_unit_id'] = operating_unit.id
        return vals, config
