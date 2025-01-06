# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import requests
from odoo import _, api, models


_logger = logging.getLogger(__file__)


class AccountInvoiceImportSimplePdfMixin(models.AbstractModel):
    _inherit = "account.invoice.import.simple.pdf.mixin"

    @api.model
    def simple_pdf_text_extraction(self, file_data, test_info):
        ocrmypdf_host = self.env['ir.config_parameter'].sudo().get_param(
            'account_edi_simple_pdf.ocrmypdf_host', 'http://ocrmypdf:5000',
        )
        ocrmypdf_params = self.env['ir.config_parameter'].sudo().get_param(
            'account_edi_simple_pdf.ocrmypdf_params', '--redo-ocr',
        )
        _logger.info('Running ocr on %s with parameters %s', ocrmypdf_host, ocrmypdf_params)
        response = None
        try:
            response = requests.post(
                ocrmypdf_host,
                data={'params': ocrmypdf_params},
                files={'file': ('file.pdf', file_data)},
            )
        except requests.exceptions.ConnectionError:
            _logger.error('Error connecting to %s', ocrmypdf_host)

        if response is None:
            _logger.error('Continue without ocr')
        elif response.status_code == 400:
            _logger.error(response.text)
            _logger.error('Continue without ocr')
        else:
            file_data = response.content
        return super().simple_pdf_text_extraction(file_data, test_info)
