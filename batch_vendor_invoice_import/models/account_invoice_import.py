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
        if self.task_id:
            assert parsed_inv.get('pre-processed'), 'pre-processing not done'
            aio = self.env['account.invoice']
            ailo = self.env['account.invoice.line']
            bdio = self.env['business.document.import']
            rpo = self.env['res.partner']
            company = self.company_id or False
            start_end_dates_installed = hasattr(ailo, 'start_date') and \
                                        hasattr(ailo, 'end_date')
            if parsed_inv['type'] in ('out_invoice', 'out_refund'):
                partner_type = 'customer'
            else:
                partner_type = 'supplier'
            if parsed_inv['partner'].get('default_supplier') and parsed_inv['partner']['default_supplier'] == True and company:
                partner = rpo.search([('default_supplier','=', True),('company_id','=', company.id)])
            else:
                partner = bdio._match_partner(
                parsed_inv['partner'], parsed_inv['chatter_msg'],
                partner_type=partner_type)
            partner = partner.commercial_partner_id
            currency = bdio._match_currency(
                parsed_inv.get('currency'), parsed_inv['chatter_msg'])
            vals = {
                'partner_id': partner.id,
                'currency_id': currency.id,
                'type': parsed_inv['type'],
                'company_id': company.id,
                'origin': parsed_inv.get('origin'),
                'reference': parsed_inv.get('invoice_number'),
                'date_invoice': parsed_inv.get('date'),
                'journal_id':
                    aio.with_context(type=parsed_inv['type'])._default_journal().id,
                'invoice_line_ids': [],
            }
            vals = aio.play_onchanges(vals, ['partner_id'])
            vals['invoice_line_ids'] = []
            # Force due date of the invoice
            if parsed_inv.get('date_due'):
                vals['date_due'] = parsed_inv.get('date_due')
            # Bank info
            if parsed_inv.get('iban'):
                partner = rpo.browse(vals['partner_id'])
                partner_bank = bdio._match_partner_bank(
                    partner, parsed_inv['iban'], parsed_inv.get('bic'),
                    parsed_inv['chatter_msg'], create_if_not_found=True)
                if partner_bank:
                    vals['partner_bank_id'] = partner_bank.id
            config = import_config  # just to make variable name shorter
            if not config:
                config = partner.invoice_import2import_config()

            if config['invoice_line_method'].startswith('1line'):
                if config['invoice_line_method'] == '1line_no_product':
                    if config['taxes']:
                        invoice_line_tax_ids = [(6, 0, config['taxes'].ids)]
                    else:
                        invoice_line_tax_ids = False
                    il_vals = {
                        'account_id': config['account'].id,
                        'invoice_line_tax_ids': invoice_line_tax_ids,
                        'price_unit': parsed_inv.get('amount_untaxed'),
                    }
                elif config['invoice_line_method'] == '1line_static_product':
                    product = config['product']
                    il_vals = {'product_id': product.id, 'invoice_id': vals}
                    il_vals = ailo.play_onchanges(il_vals, ['product_id'])
                    il_vals.pop('invoice_id')
                if config.get('label'):
                    il_vals['name'] = config['label']
                elif parsed_inv.get('description'):
                    il_vals['name'] = parsed_inv['description']
                elif not il_vals.get('name'):
                    il_vals['name'] = _('MISSING DESCRIPTION')
                self.set_1line_price_unit_and_quantity(il_vals, parsed_inv)
                self.set_1line_start_end_dates(il_vals, parsed_inv)
                vals['invoice_line_ids'].append((0, 0, il_vals))
            elif config['invoice_line_method'].startswith('nline'):
                if not parsed_inv.get('lines'):
                    raise UserError(_(
                        "You have selected a Multi Line method for this import "
                        "but Odoo could not extract/read any XML file inside "
                        "the PDF invoice."))
                if config['invoice_line_method'] == 'nline_no_product':
                    static_vals = {
                        'account_id': config['account'].id,
                    }
                elif config['invoice_line_method'] == 'nline_static_product':
                    sproduct = config['product']
                    static_vals = {'product_id': sproduct.id, 'invoice_id': vals}
                    static_vals = ailo.play_onchanges(static_vals, ['product_id'])
                    static_vals.pop('invoice_id')
                else:
                    static_vals = {}
                for line in parsed_inv['lines']:
                    il_vals = static_vals.copy()
                    if config['invoice_line_method'] == 'nline_auto_product':
                        product = bdio._match_product(
                            line['product'], parsed_inv['chatter_msg'],
                            seller=partner)
                        il_vals = {'product_id': product.id, 'invoice_id': vals}
                        il_vals = ailo.play_onchanges(il_vals, ['product_id'])
                        il_vals.pop('invoice_id')
                    elif config['invoice_line_method'] == 'nline_no_product':
                        taxes = bdio._match_taxes(
                            line.get('taxes'), parsed_inv['chatter_msg'])
                        il_vals['invoice_line_tax_ids'] = [(6, 0, taxes.ids)]
                    if line.get('name'):
                        il_vals['name'] = line['name']
                    elif not il_vals.get('name'):
                        il_vals['name'] = _('MISSING DESCRIPTION')
                    if start_end_dates_installed:
                        il_vals['start_date'] = \
                            line.get('date_start') or parsed_inv.get('date_start')
                        il_vals['end_date'] = \
                            line.get('date_end') or parsed_inv.get('date_end')
                    uom = bdio._match_uom(
                        line.get('uom'), parsed_inv['chatter_msg'])
                    il_vals['uom_id'] = uom.id
                    il_vals.update({
                        'quantity': line['qty'],
                        'price_unit': line['price_unit'],  # TODO fix for tax incl
                    })
                    vals['invoice_line_ids'].append((0, 0, il_vals))
            # Write analytic account + fix syntax for taxes
            aacount_id = config.get('account_analytic') and \
                         config['account_analytic'].id or False
            if aacount_id:
                for line in vals['invoice_line_ids']:
                    line[2]['account_analytic_id'] = aacount_id
            vals['company_id'] = company.id or False
            vals['operating_unit_id'] = self.operating_unit_id.id or False
            return (vals, config)

        else:
            return super(AccountInvoiceImport, self)._prepare_create_invoice_vals(parsed_inv,
                                                                                         import_config)

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
                invoice2data_res = {}
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
