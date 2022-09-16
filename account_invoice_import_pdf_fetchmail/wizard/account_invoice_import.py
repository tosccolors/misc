

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from lxml import etree
import logging
import requests
import base64
import mimetypes

logger = logging.getLogger(__name__)


class AccountInvoiceImport(models.TransientModel):
    _inherit = 'account.invoice.import'

    # Overridden:
    @api.model
    def parse_invoice(self, invoice_file_b64, invoice_filename):
        assert invoice_file_b64, 'No invoice file'
        logger.info('Starting to import invoice %s', invoice_filename)
        file_data = base64.b64decode(invoice_file_b64)
        filetype = mimetypes.guess_type(invoice_filename)
        logger.debug('Invoice mimetype: %s', filetype)

        if filetype and filetype[0] in ['application/xml', 'text/xml']:
            try:
                xml_root = etree.fromstring(file_data)
            except Exception as e:
                raise UserError(_(
                    "This XML file is not XML-compliant. Error: %s") % e)
            pretty_xml_string = etree.tostring(
                xml_root, pretty_print=True, encoding='UTF-8',
                xml_declaration=True)
            logger.debug('Starting to import the following XML file:')
            logger.debug(pretty_xml_string)
            parsed_inv = self.parse_xml_invoice(xml_root)
            if parsed_inv is False:
                raise UserError(_(
                    "This type of XML invoice is not supported. "
                    "Did you install the module to support this type "
                    "of file?"))
        # Fallback on PDF
        else:
            ctx = self._context.copy()
            ctx.update({'invoice_filename': invoice_filename
                        , 'filetype': filetype})
            parsed_inv = self.with_context(ctx).parse_pdf_invoice(file_data)
        if 'attachments' not in parsed_inv:
            parsed_inv['attachments'] = {}
        parsed_inv['attachments'][invoice_filename] = invoice_file_b64
        # pre_process_parsed_inv() will be called again a second time,
        # but it's OK
        pp_parsed_inv = self.pre_process_parsed_inv(parsed_inv)
        return pp_parsed_inv

    # Overridden:
    @api.model
    def parse_pdf_invoice(self, file_data):
        '''This method must be inherited by additional modules with
        the same kind of logic as the account_bank_statement_import_*
        modules'''
        ocred_pdf = ''
        bdio = self.env['business.document.import']
        xml_files_dict = bdio.get_xml_files_from_pdf(file_data)
        for xml_filename, xml_root in xml_files_dict.items():
            logger.info('Trying to parse XML file %s', xml_filename)
            parsed_inv = self.parse_xml_invoice(xml_root)
            if parsed_inv:
                return parsed_inv

        invoice_filename = self._context.get('invoice_filename')
        filetype = self._context.get('filetype')

        # Try OCR
        if not xml_files_dict and (filetype and filetype[0] == 'application/pdf'):
            logger.info('Trying to perform OCR on pdf file %s', invoice_filename)
            ioFile = '/tmp/' + str(invoice_filename)
            with open(ioFile, 'wb') as f:
                f.write(file_data)

            files = {
                'params': (None, '--force-ocr'),
                'file': open(ioFile, 'rb'),
            }
            params = self.env['ir.config_parameter'].sudo()
            OCRendpoint = params.get_param('invoice_import_simple_pdf_fetchmail.ocr_endpoint')
            if not OCRendpoint:
                raise UserError(_(
                    "OCR Endpoint is not set in the Configuration"))

            response = requests.post(OCRendpoint, files=files)
            if response.status_code == 200:
                file_data = ocred_pdf = response.content
                logger.info('Invoice pdf has been successfully OCRed %s', invoice_filename)
            else:
                logger.info('Failed to perform OCR on %s', invoice_filename)

        parsed_inv = self.fallback_parse_pdf_invoice(file_data)
        if not parsed_inv:
            raise UserError(_(
                "This type of PDF invoice is not supported. Did you install "
                "the module to support this type of file?"))

        # Updated OCRed File
        if ocred_pdf:
            parsed_inv['ocred_pdf'] = ocred_pdf
            parsed_inv['ocred_pdf_name'] = invoice_filename

        return parsed_inv
