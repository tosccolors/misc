# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, tools, fields, _
from odoo.exceptions import UserError
import os
from tempfile import mkstemp
import pkg_resources
import logging
logger = logging.getLogger(__name__)

try:
    from invoice2data.main import extract_data
    from invoice2data.template import read_templates
    from invoice2data.main import logger as loggeri2data
except ImportError:
    logger.debug('Cannot import invoice2data')


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    task_id = fields.Many2one('external.file.task', string="Import Task", readonly=True)


    @api.multi
    def create_invoice_action(self, parsed_inv=None):
        '''parsed_inv is not a required argument'''
        self.ensure_one()
        if self.task_id:
            if parsed_inv is None:
                parsed_inv = self.parse_invoice()
            invoice = self.create_invoice(parsed_inv)
            invoice.message_post(_(
                "This invoice has been created automatically via file import"))
            return True
        else:
            return super(AccountInvoiceImport, self).create_invoice_action(parsed_inv=None)


    @api.model
    def invoice2data_parse_invoice(self, file_data):
        if not self.task_id:
            self.invoice2data_to_parsed_inv(super(AccountInvoiceImport, self).invoice2data_parse_invoice(file_data))
        else:

            logger.info('Trying to analyze PDF invoice with invoice2data lib')
            fd, file_name = mkstemp()
            try:
                os.write(fd, file_data)
            finally:
                os.close(fd)
            # Transfer log level of Odoo to invoice2data
            loggeri2data.setLevel(logger.getEffectiveLevel())
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
                templates += read_templates(
                    pkg_resources.resource_filename('invoice2data', 'templates'))
            logger.debug(
                'Calling invoice2data.extract_data with templates=%s',
                templates)
            try:
                invoice2data_res = extract_data(file_name, templates=templates)
            except Exception:
                invoice2data_res = {}
                invoice2data_res['vat'] = 'PDF Invoice parsing failed.'
            if not invoice2data_res:
                invoice2data_res = {}
                invoice2data_res['vat'] = 'This PDF invoice doesn\'t match a known template of the invoice2data lib.'
            logger.info('Result of invoice2data PDF extraction: %s', invoice2data_res)
            return self.invoice2data_to_parsed_inv(invoice2data_res)

    @api.model
    def invoice2data_to_parsed_inv(self, invoice2data_res):
        if invoice2data_res['vat'] == 'PDF Invoice parsing failed.' or \
           invoice2data_res['vat'] == 'This PDF invoice doesn\'t match a known template of the invoice2data lib.':
            parsed_inv = {
                'partner': {
                    'name':'Dummy',
                },
                'description': invoice2data_res.get('vat') or '',
                'amount_total': 0.0,
                'invoice_number': False,
                'date': False,
                'date_due': False,
                'date_start': False,
                'date_end': False,
            }
        else:
            parsed_inv = {
                'partner': {
                    'vat': invoice2data_res.get('vat'),
                    'name': invoice2data_res.get('partner_name'),
                    'email': invoice2data_res.get('partner_email'),
                    'website': invoice2data_res.get('partner_website'),
                    'siren': invoice2data_res.get('siren'),
                    },
                'currency': {
                    'iso': invoice2data_res.get('currency'),
                    },
                'amount_total': invoice2data_res.get('amount'),
                'invoice_number': invoice2data_res.get('invoice_number'),
                'date': invoice2data_res.get('date'),
                'date_due': invoice2data_res.get('date_due'),
                'date_start': invoice2data_res.get('date_start'),
                'date_end': invoice2data_res.get('date_end'),
                'description': invoice2data_res.get('description'),
                }
            if 'amount_untaxed' in invoice2data_res:
                parsed_inv['amount_untaxed'] = invoice2data_res['amount_untaxed']
            if 'amount_tax' in invoice2data_res:
                parsed_inv['amount_tax'] = invoice2data_res['amount_tax']
        return parsed_inv
