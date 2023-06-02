# -*- coding: utf-8 -*-
import pdb
from base64 import b64decode
from io import BytesIO
from logging import getLogger

from PIL import Image

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

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


class Company(models.Model):
    _inherit = "res.company"

    pdf_background_image = fields.Binary("Background Image Pdf", help="Upload an background image in Pdf format.")



class Report(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
        logger.info("\n\n\nCame to pdf_bg %s, %s"%(res_ids, self.env.context.get("res_ids")))
        Model = self.env[self.model]
        record_ids = Model.browse(res_ids)
        company_id = False
        if record_ids[:1]._name == "res.company":
            company_id = record_ids[:1]
        # Fix test cases error. #22107
        elif hasattr(record_ids[:1], "company_id"):
            # If in record company is not set then consider current log in
            # user's company. #22476
            company_id = record_ids[:1].company_id or self.env.user.company_id
        else:
            company_id = self.env.company

        if not self.env.context.get("res_ids"):
            return super(Report, self.with_context(res_ids=res_ids, bg_company=company_id))._render_qweb_pdf(
                res_ids=res_ids, data=data
            )

        return super(Report, self).with_context(bg_company=company_id)._render_qweb_pdf(res_ids=res_ids, data=data)

    @api.model
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None,
                         set_viewport_size=False,):

        logger.info("\n\n\nCame to pdf_bg | _run_wkhtmltopdf %s"%(self.env.context.get("res_ids", False)))

        result = super(Report, self)._run_wkhtmltopdf(
            bodies,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        # docids = self.env.context.get("res_ids", False)
        backgroungImg = None
        company_bg = self._context.get("bg_company")
        background_img = (company_bg.pdf_background_image)

        if background_img:
            # watermark = b64decode(self.pdf_watermark)
            backgroungImg = b64decode(background_img)

        # elif docids:
        #     watermark = safe_eval(
        #         self.pdf_watermark_expression or "None",
        #         dict(env=self.env, docs=self.env[self.model].browse(docids)),
        #     )
        #     if watermark:
        #         watermark = b64decode(watermark)

        if not backgroungImg:
            return result

        pdf = PdfFileWriter()
        pdf_bgImg = None
        try:
            pdf_bgImg = PdfFileReader(BytesIO(backgroungImg))
        except PdfReadError:
            # let's see if we can convert this with pillow
            try:
                Image.init()
                image = Image.open(BytesIO(backgroungImg))
                pdf_buffer = BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")
                resolution = image.info.get("dpi", self.paperformat_id.dpi or 90)
                if isinstance(resolution, tuple):
                    resolution = resolution[0]
                image.save(pdf_buffer, "pdf", resolution=resolution)
                pdf_bgImg = PdfFileReader(pdf_buffer)
            except Exception as e:
                logger.exception("Failed to load background Image", e)

        if not pdf_bgImg:
            logger.error("No usable background image found, got %s...", backgroungImg[:100])
            return result

        if pdf_bgImg.numPages < 1:
            logger.error("Your background pdf does not contain any pages")
            return result
        if pdf_bgImg.numPages > 1:
            logger.debug(
                "Your background pdf contains more than one page, "
                "all but the first one will be ignored"
            )

        for page in PdfFileReader(BytesIO(result)).pages:
            bg_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            bg_page.mergePage(pdf_bgImg.getPage(0))
            bg_page.mergePage(page)

        pdf_content = BytesIO()
        pdf.write(pdf_content)

        return pdf_content.getvalue()
