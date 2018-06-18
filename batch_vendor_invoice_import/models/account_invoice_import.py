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
    user_id = fields.Many2one(related='task_id.user_id',)

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
        if self.task_id and self.company_id and self.user_id:
            return super(AccountInvoiceImport, self).sudo(self.user_id)._prepare_create_invoice_vals(parsed_inv, import_config=import_config)
        return super(AccountInvoiceImport, self)._prepare_create_invoice_vals(parsed_inv, import_config=import_config)

    @api.model
    def invoice2data_parse_invoice(self, file_data):
        if not self.task_id:
            return super(AccountInvoiceImport, self).invoice2data_parse_invoice(file_data)
        else:
            invoice2data_res = self.invoice2data_parse_invoice_batch(file_data)
            if invoice2data_res.get('pdf_failed', False) and self.paired_id:
                file_data_2 = self.paired_id.datas.decode('base64')
                invoice2data_res = self.invoice2data_parse_invoice_batch(file_data_2)
            return self.invoice2data_to_parsed_inv(invoice2data_res)

    @api.model
    def invoice2data_parse_invoice_batch(self, file_data):
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
            invoice2data_res['pdf_failed'] = 'PDF Invoice parsing failed.'
        if not invoice2data_res:
            invoice2data_res = {}
            invoice2data_res['pdf_failed'] = 'This PDF invoice doesn\'t match a known template of the invoice2data lib.'
        logger.info('Result of invoice2data batch PDF extraction: %s', invoice2data_res)
        return invoice2data_res

    @api.model
    def invoice2data_to_parsed_inv(self, invoice2data_res):
        if self.task_id and (invoice2data_res.get('pdf_failed', False) == 'PDF Invoice parsing failed.'\
                            or invoice2data_res.get('pdf_failed', False) == 'This PDF invoice doesn\'t match a known'
                                                                            ' template of the invoice2data lib.'):
            parsed_inv = {
                    'partner': {
                        'default_supplier':True,
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

    @api.model
    def pre_process_parsed_inv(self, parsed_inv):
        if parsed_inv.get('pre-processed'):
            return parsed_inv
        parsed_inv['pre-processed'] = True
        if 'chatter_msg' not in parsed_inv:
            parsed_inv['chatter_msg'] = []
        if parsed_inv.get('type') in ('out_invoice', 'out_refund'):
            return parsed_inv
        prec_ac = self.env['decimal.precision'].precision_get('Account')
        prec_pp = self.env['decimal.precision'].precision_get('Product Price')
        prec_uom = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        if 'amount_tax' in parsed_inv and 'amount_untaxed' not in parsed_inv:
            parsed_inv['amount_untaxed'] = \
                parsed_inv['amount_total'] - parsed_inv['amount_tax']
        elif (
                'amount_untaxed' not in parsed_inv and
                'amount_tax' not in parsed_inv):
            # For invoices that never have taxes
            parsed_inv['amount_untaxed'] = parsed_inv['amount_total']
        # Support the 2 refund methods; if method a) is used, we convert to
        # method b)
        if not parsed_inv.get('type'):
            parsed_inv['type'] = 'in_invoice'  # default value
        if (
                parsed_inv['type'] == 'in_invoice' and
                float_compare(
                    parsed_inv['amount_total'], 0, precision_digits=prec_ac) < 0):
            parsed_inv['type'] = 'in_refund'
            for entry in ['amount_untaxed', 'amount_total']:
                parsed_inv[entry] *= -1
            for line in parsed_inv.get('lines', []):
                line['qty'] *= -1
                if 'price_subtotal' in line:
                    line['price_subtotal'] *= -1
        # Rounding work
        for entry in ['amount_untaxed', 'amount_total']:
            parsed_inv[entry] = float_round(
                parsed_inv[entry], precision_digits=prec_ac)
        for line in parsed_inv.get('lines', []):
            line['qty'] = float_round(line['qty'], precision_digits=prec_uom)
            line['price_unit'] = float_round(
                line['price_unit'], precision_digits=prec_pp)
        log_parsed_inv = {x: parsed_inv[x] for x in parsed_inv if x not in ('attachments')}
        logger.debug('Result of invoice parsing parsed_inv=%s', log_parsed_inv)
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