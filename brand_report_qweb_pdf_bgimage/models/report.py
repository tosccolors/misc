# -*- coding: utf-8 -*-
from logging import getLogger

from odoo import api, fields, models

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    pass

logger = getLogger(__name__)

try:
    from PyPDF2 import PdfFileReader, PdfFileWriter  # pylint: disable=W0404
    from PyPDF2.utils import PdfReadError  # pylint: disable=W0404
except ImportError:
    logger.debug("Can not import PyPDF2")


class Brand(models.Model):
    _inherit = "res.brand"

    pdf_background_image = fields.Binary("Background Image Pdf", help="Upload a background image in Pdf format.")



class Report(models.Model):
    _inherit = "ir.actions.report"


    def _get_background_image(self):
        bg_source = None
        docids = self.env.context.get("res_ids", False)

        try:
            if docids:
                docs = self.env[self.model].browse(docids)
                bg_source = docs.brand_id
        except:
            pass

        return super(Report, self.with_context(bg_source=bg_source))._get_background_image()
