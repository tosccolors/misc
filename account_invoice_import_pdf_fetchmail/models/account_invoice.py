# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
import base64
import logging

_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = ["account.invoice"]

    def _import_invoice_from_attachment(self, invoice, msg_dict, custom_values=None):
        InvImport = self.env['account.invoice.import']
        bdio = self.env['business.document.import']

        _logger.info(
            'New email received associated with account.invoice.import: '
            'From: %s, Subject: %s, Date: %s, Message ID: %s. Executing '
            'with user %s ID %d',
            msg_dict.get('email_from'), msg_dict.get('subject'),
            msg_dict.get('date'), msg_dict.get('message_id'),
            self.env.user.name, self.env.user.id)
        # It seems that the "Odoo-way" to handle multi-company in E-mail
        # gateways is by using mail.aliases associated with users that
        # don't switch company (I haven't found any other way), which
        # is not convenient because you may have to create new users
        # for that purpose only. So I implemented my own mechanism,
        # based on the destination email address.
        # This method is called (indirectly) by the fetchmail cron which
        # is run by default as admin and retreive all incoming email in
        # all email accounts. We want to keep this default behavior,
        # and, in multi-company environnement, differentiate the company
        # per destination email address
        company_id = False
        parsed_inv, partner = {}, False
        all_companies = self.env['res.company'].search_read(
            [], ['invoice_import_email'])
        if len(all_companies) > 1:  # multi-company setup
            for company in all_companies:
                if company['invoice_import_email']:
                    company_dest_email = company['invoice_import_email'] \
                        .strip()
                    if (
                        company_dest_email in msg_dict.get('to', '') or
                        company_dest_email in msg_dict.get('cc', '')):
                        company_id = company['id']
                        _logger.info(
                            'Matched with %s: importing invoices in company '
                            'ID %d', company_dest_email, company_id)
                        break
            if not company_id:
                _logger.error(
                    'Invoice import mail gateway in multi-company setup: '
                    'invoice_import_email of the companies of this DB was '
                    'not found as destination of this email (to: %s, cc: %s). '
                    'Ignoring this email.',
                    msg_dict['email_to'], msg_dict['cc'])
                return
        else:  # mono-company setup
            company_id = all_companies[0]['id']

        self = self.with_context(force_company=company_id)

        i = 0
        if msg_dict.get('attachments'):
            i += 1
            for attach in msg_dict['attachments']:
                try:
                    _logger.info(
                        'Attachment %d: %s. Trying to import it as an invoice',
                        i, attach.fname)

                    parsed_inv = InvImport.parse_invoice(
                        base64.b64encode(attach.content), attach.fname)

                    partner = bdio._match_partner(
                        parsed_inv['partner'], parsed_inv['chatter_msg'])

                    existing_inv = InvImport.invoice_already_exists(partner, parsed_inv)
                    if existing_inv:
                        _logger.warning(
                            "Mail import: this supplier invoice already exists "
                            "in Odoo (ID %d number %s supplier number %s)",
                            existing_inv.id, existing_inv.number,
                            parsed_inv.get('invoice_number'))
                        continue
                    import_configs = InvImport._search_import_config(
                        partner, company_id)
                    if not import_configs:
                        _logger.warning(
                            "Mail import: missing Invoice Import Configuration "
                            "for partner '%s'.", partner.display_name)
                        continue
                    elif len(import_configs) == 1:
                        import_config = import_configs.convert_to_import_config()
                    else:
                        _logger.info(
                            "There are %d invoice import configs for partner %s. "
                            "Using the first one '%s''", len(import_configs),
                            partner.display_name, import_configs[0].name)
                        import_config = \
                            import_configs[0].convert_to_import_config()

                    parsed_inv = InvImport.pre_process_parsed_inv(parsed_inv)
                    (Ivals, ic) = InvImport._prepare_create_invoice_vals(parsed_inv, import_config)
                    invoice.write(Ivals)
                    invoice.compute_taxes()
                    InvImport.post_process_invoice(parsed_inv, invoice, import_config)
                    bdio.post_create_or_update(parsed_inv, invoice)

                except:
                    _logger.info(
                        'Attachment %d: %s. Failed to import it as an invoice',
                        i, attach.fname)
                    pass
                _logger.info('Invoice ID %d created from email', invoice.id)
                invoice.message_post(body=_(
                    "Invoice successfully imported from email sent by "
                    "<b>%s</b> on %s with subject <i>%s</i>.") % (
                                              msg_dict.get('email_from'), msg_dict.get('date'),
                                              msg_dict.get('subject')))
                if 'ocred_pdf' in parsed_inv:
                    filename = parsed_inv['ocred_pdf_name']
                    ocr_fname = '%s-OCR.pdf' % filename.split('.pdf')[0]

                    attachment_id = self.env['ir.attachment'].create({
                        'name': ocr_fname,
                        'type': 'binary',
                        'datas': base64.b64encode(parsed_inv['ocred_pdf']),
                        'datas_fname': ocr_fname,
                        'store_fname': ocr_fname.split('.pdf')[0],
                        'res_model': 'account.invoice',
                        'res_id': invoice.id,
                        'mimetype': 'application/pdf'
                    })
                    invoice.message_post(body=_("%s : This Pdf has been successfully OCRed."%filename),
                                         attachment_ids=[attachment_id.id])

                # Exit loop: after reading a valid Invoice pdf attachment.
                if partner:
                    break
        else:
            _logger.info('The email has no attachments, skipped.')

        return True

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        ''' Inherited to call Pdf Processing'''
        invoice = super(AccountInvoice, self).message_new(msg_dict, custom_values)
        self._import_invoice_from_attachment(invoice, msg_dict)
        return invoice
