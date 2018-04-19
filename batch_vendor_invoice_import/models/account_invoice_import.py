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
    company_id = fields.Many2one('res.company', )
    operating_unit_id = fields.Many2one('operating.unit', )
    paired_id = fields.Many2one('ir.attachment.metadata', string='Paired Exported Attachment')

    @api.multi
    def parse_invoice(self):
        parsed_inv = super(AccountInvoiceImport, self).parse_invoice()
        if self.paired_id:
            parsed_inv['attachments'][self.paired_id.name] = self.paired_id.datas
        return parsed_inv

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
            return super(AccountInvoiceImport, self).create_invoice_action(parsed_inv)

    @api.model
    def _prepare_create_invoice_vals(self, parsed_inv, import_config=False):
        (vals, import_config) = super(AccountInvoiceImport, self)._prepare_create_invoice_vals(parsed_inv, import_config)
        if self.task_id:
            vals['company_id'] = self.company_id.id or False
            vals['operating_unit_id'] = self.operating_unit_id.id or False
        return (vals, import_config)

    @api.model
    def invoice2data_parse_invoice(self, file_data):
        if not self.task_id:
            return super(AccountInvoiceImport, self).invoice2data_parse_invoice(file_data)

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
                invoice2data_res['pdf_failed'] = 'PDF Invoice parsing failed.'
            if not invoice2data_res:
                invoice2data_res = {}
                invoice2data_res['pdf_failed'] = 'This PDF invoice doesn\'t match a known template of the invoice2data lib.'
            logger.info('Result of invoice2data batch PDF extraction: %s', invoice2data_res)
            return self.invoice2data_to_parsed_inv(invoice2data_res)

    @api.model
    def invoice2data_to_parsed_inv(self, invoice2data_res):
        if self.task_id and (invoice2data_res.get('pdf_failed', False) == 'PDF Invoice parsing failed.'\
                            or invoice2data_res.get('pdf_failed', False) == 'This PDF invoice doesn\'t match a known'
                                                                            ' template of the invoice2data lib.'):
            parsed_inv = {
                    'partner': {
                        'name':'Dummy',
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
