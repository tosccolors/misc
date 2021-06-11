# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, exceptions, models, _
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
        return result

    @api.model
    def _account_invoice_import_ml_add_email(self, partner, email, data):
        # never create a new partner, leave this as manual step
        data.setdefault('__import_ml_warnings', []).append(_(
            'Please check unknown email address %s and add to vendor below'
        ) % email)

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
            vals['source_email'] = ','.join(email_split(msg_dict.get('email_from', '')))
        return vals, config

    @api.model
    def invoice_import_direct(self, invoice_b64, invoice_filename, raise_if_fail=True):
        # we only ever want to import pdf or xml files
        invoice_filename = invoice_filename or ''
        if not invoice_filename.endswith('.xml') and\
                not invoice_filename.endswith('.pdf'):
            return False
        try:
            # super will fail for unknown xml files
            return super(AccountInvoiceImport, self).invoice_import_direct(
                invoice_b64, invoice_filename, raise_if_fail=raise_if_fail,
            )
        except exceptions.UserError:
            # be sure to always import an invoice if we got a file
            msg_dict = self.env.context.get(
                'account_invoice_import_ml_msg_dict', {}
            )
            if not msg_dict:
                return False

            try:
                partner = self.env['business.document.import']._match_partner(
                    dict(email=msg_dict.get('email_from')), '',
                )
            except exceptions.UserError:
                partner = self.env.ref('account_invoice_import_ml.unknown_supplier')

            invoice_id = self.env['account.invoice'].message_new(
                msg_dict, custom_values=dict(partner_id=partner.id),
            )

            if not invoice_id:
                return False

            invoice = self.env['account.invoice'].browse(invoice_id)

            for attachment in msg_dict.get('attachments', {}):
                self.env['ir.attachment'].create({
                    'name': invoice_filename,
                    'res_id': invoice.id,
                    'res_model': invoice._name,
                    'datas': attachment.content.encode('base64'),
                    'datas_fname': invoice_filename,
                })

            return invoice
