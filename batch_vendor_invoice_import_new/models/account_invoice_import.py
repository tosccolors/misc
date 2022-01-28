# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, tools, fields, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round, float_is_zero
import os
from tempfile import mkstemp
import pkg_resources
import logging
import io
logger = logging.getLogger(__name__)

try:
    from invoice2data.main import extract_data
    from invoice2data.extract.loader import read_templates
    from invoice2data.main import logger as loggeri2data

    # Transfer log level of Odoo to invoice2data
    loggeri2data.setLevel(logging.DEBUG)

except ImportError:
    logger.debug('Cannot import invoice2data')


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    task_id = fields.Many2one('external.file.task', string="Import Task", readonly=True)
    company_id = fields.Many2one('res.company', )
    operating_unit_id = fields.Many2one('operating.unit', )
    user_id = fields.Many2one(related='task_id.user_id',)

    @api.multi
    def import_invoice(self):
        """Original Method called by the button of the wizard
        (import step AND config step). This one is called by _run in
        IrAttachmentMetadata"""
        if not self.task_id:
            action = super(AccountInvoiceImport, self).import_invoice()
        else:
            self.ensure_one()
            aio = self.env['account.invoice']
            aiico = self.env['account.invoice.import.config']
            bdio = self.env['business.document.import']
            company_id = self.company_id.id
            parsed_inv = self.parse_invoice(
                self.invoice_file, self.invoice_filename)
            partner = bdio._match_partner(
                parsed_inv['partner'], parsed_inv['chatter_msg'])
            partner = partner.commercial_partner_id
            currency = bdio._match_currency(
                parsed_inv.get('currency'), parsed_inv['chatter_msg'])
            parsed_inv['partner']['recordset'] = partner
            parsed_inv['currency']['recordset'] = currency
            existing_inv = self.invoice_already_exists(partner, parsed_inv)
            if existing_inv:
                raise UserError(_(
                    "This invoice already exists in Odoo. It's "
                    "Supplier Invoice Number is '%s' and it's Odoo number "
                    "is '%s'")
                                % (parsed_inv.get('invoice_number'), existing_inv.number))
            import_configs = aiico.search([
                ('partner_id', '=', partner.id),
                ('company_id', '=', company_id)])
            if not import_configs:
                raise UserError(_(
                    "Missing Invoice Import Configuration on partner '%s'.")
                                % partner.display_name)
            else:
                import_config = import_configs[0].convert_to_import_config()
            action = self.create_invoice_action(parsed_inv, import_config)
        return action

    @api.multi
    def create_invoice_action(self, parsed_inv=None, import_config=None):
        '''parsed_inv is not a required argument'''

        if not self.task_id:
            return super(AccountInvoiceImport, self).create_invoice_action(parsed_inv, import_config)
        else:
            self.ensure_one()
            if parsed_inv is None:
                parsed_inv = self.parse_invoice(
                    self.invoice_file, self.invoice_filename)
            if import_config is None:
                assert self.import_config_id
                import_config = self.import_config_id.convert_to_import_config()
            invoice = self.create_invoice(parsed_inv, import_config)
            invoice.message_post(_(
                "This invoice has been created automatically via batch file import"))
        return True

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config=False):
        (vals, config) = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(parsed_inv, import_config=import_config)
        if self.task_id:
            vals['operating_unit_id'] = self.operating_unit_id.id or False
        return (vals, config)

    @api.model
    def invoice2data_parse_invoice(self, file_data):
        logger.info('Trying to analyze PDF invoice with invoice2data lib')
        log_capture_string = io.StringIO()
        ch = logging.StreamHandler(log_capture_string)
        ch.setLevel(logging.DEBUG)
        loggeri2data.addHandler(ch)
        fd, file_name = mkstemp()
        try:
            os.write(fd, file_data)
        finally:
            os.close(fd)

        local_templates_dir = tools.config.get(
            'invoice2data_templates_dir', False)
        logger.debug(
            'invoice2data local_templates_dir=%s', local_templates_dir)
        templates = []
        if local_templates_dir and os.path.isdir(local_templates_dir):
            templates += read_templates(local_templates_dir)
        exclude_built_in_templates = tools.config.get(
            'invoice2data_exclude_built_in_templates', False)
        if not exclude_built_in_templates:
            templates += read_templates()
        logger.debug(
            'Calling invoice2data.extract_data with templates=%s',
            templates)
        if not self.task_id:
            try:
                invoice2data_res = extract_data(file_name, templates=templates)
                log_contents = log_capture_string.getvalue()
#                log_capture_string.close()
            except Exception as e:
                raise UserError(_(
                    "PDF Invoice parsing failed. Error message: %s") % e)
            if not invoice2data_res:
                raise UserError(_(
                    "This PDF invoice either doesn't match "
                    "a known template of the invoice2data lib (no key match) "
                    "or field(s) couldn't be matched."
                    "\nParsed invoice data (space replaced by tilde):\n") + log_contents.replace(" ","\x7E"))
            logger.info(
                'Result of invoice2data PDF extraction: %s', invoice2data_res)
        else:
            try:
                invoice2data_res = extract_data(file_name, templates=templates)
                log_contents = log_capture_string.getvalue()
#                log_capture_string.close()
            except Exception:
                invoice2data_res = {}
                invoice2data_res['pdf_failed'] = 'PDF Invoice parsing failed.'
            if not invoice2data_res:
                invoice2data_res = {}
                invoice2data_res[
                    'pdf_failed'] = 'This PDF invoice doesn\'t match a known template of the invoice2data lib.'
            logger.info(
                'Result of invoice2data batch PDF extraction: %s', invoice2data_res)
        return self.invoice2data_to_parsed_inv(invoice2data_res)

    @api.model
    def invoice2data_to_parsed_inv(self, invoice2data_res):
        if self.task_id and (invoice2data_res.get('pdf_failed', False) == 'PDF Invoice parsing failed.' \
                            or invoice2data_res.get('pdf_failed', False) == 'This PDF invoice doesn\'t match a known'
                                                                            ' template of the invoice2data lib.'):
            parsed_inv = {
                    'partner': {
                        'default_supplier':True,
                    },
                    'currency': {
                        'iso': False,
                    },
                    'amount_total': 0.0,
                    'invoice_number': False,
                    'date': False,
                    'date_due': False,
                    'date_start': False,
                    'date_end': False,
                    }

        else:
            parsed_inv = super(AccountInvoiceImport, self).invoice2data_to_parsed_inv(invoice2data_res)

        return parsed_inv


class BusinessDocumentImport(models.AbstractModel):
    _inherit = 'business.document.import'


    @api.model
    def _hook_match_partner(self, partner_dict, chatter_msg, domain, partner_type_label):
        rpo = self.env['res.partner']
        if partner_dict.get('default_supplier') and partner_dict['default_supplier'] == True :
            partner = rpo.search([('default_supplier', '=', True)])
            return partner
        return False
