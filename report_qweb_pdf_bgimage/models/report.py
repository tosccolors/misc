# -*- coding: utf-8 -*-
import pdb
from base64 import b64decode
from io import BytesIO
from logging import getLogger

from PIL import Image

import os
import tempfile
import subprocess
from contextlib import closing

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import find_in_path, ustr
from odoo.exceptions import UserError, AccessError


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


def _get_wkhtmltopdf_bin():
    return find_in_path("wkhtmltopdf")

class Company(models.Model):
    _inherit = "res.company"

    pdf_background_image = fields.Binary("Background Image Pdf", help="Upload a background image in Pdf format.")



class Report(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
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
    def _prepare_pdf_content(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None,
                         set_viewport_size=False,):

        '''Execute wkhtmltopdf as a subprocess in order to convert html given in input into a pdf
        document.

        :param bodies: The html bodies of the report, one per page.
        :param header: The html header of the report containing all headers.
        :param footer: The html footer of the report containing all footers.
        :param landscape: Force the pdf to be rendered under a landscape format.
        :param specific_paperformat_args: dict of prioritized paperformat arguments.
        :param set_viewport_size: Enable a viewport sized '1024x1280' or '1280x1024' depending of landscape arg.
        :return: Content of the pdf as a string
        '''
        paperformat_id = self.get_paperformat()

        # Build the base command args for wkhtmltopdf bin
        command_args = self._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size)

        files_command_args = []
        temporary_files = []
        if header:
            head_file_fd, head_file_path = tempfile.mkstemp(suffix='.html', prefix='report.header.tmp.')
            with closing(os.fdopen(head_file_fd, 'wb')) as head_file:
                head_file.write(header)
            temporary_files.append(head_file_path)
            files_command_args.extend(['--header-html', head_file_path])
        if footer:
            foot_file_fd, foot_file_path = tempfile.mkstemp(suffix='.html', prefix='report.footer.tmp.')
            with closing(os.fdopen(foot_file_fd, 'wb')) as foot_file:
                foot_file.write(footer)
            temporary_files.append(foot_file_path)
            files_command_args.extend(['--footer-html', foot_file_path])

        paths = []
        for i, body in enumerate(bodies):
            prefix = '%s%d.' % ('report.body.tmp.', i)
            body_file_fd, body_file_path = tempfile.mkstemp(suffix='.html', prefix=prefix)
            with closing(os.fdopen(body_file_fd, 'wb')) as body_file:
                body_file.write(body)
            paths.append(body_file_path)
            temporary_files.append(body_file_path)

        pdf_report_fd, pdf_report_path = tempfile.mkstemp(suffix='.pdf', prefix='report.tmp.')
        os.close(pdf_report_fd)
        temporary_files.append(pdf_report_path)

        try:
            wkhtmltopdf = [_get_wkhtmltopdf_bin()] + command_args + files_command_args + paths + [pdf_report_path]
            process = subprocess.Popen(wkhtmltopdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            err = ustr(err)

            if process.returncode not in [0, 1]:
                if process.returncode == -11:
                    message = _(
                        'Wkhtmltopdf failed (error code: %s). Memory limit too low or maximum file number of subprocess reached. Message : %s')
                else:
                    message = _('Wkhtmltopdf failed (error code: %s). Message: %s')
                logger.warning(message, process.returncode, err[-1000:])
                raise UserError(message % (str(process.returncode), err[-1000:]))
            else:
                if err:
                    logger.warning('wkhtmltopdf: %s' % err)
        except:
            raise

        with open(pdf_report_path, 'rb') as pdf_document:
            pdf_content = pdf_document.read()

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                logger.error('Error when trying to remove file %s' % temporary_file)

        return pdf_content

    def _get_background_image(self):
        " Fetch Brackground Image that can be used in the report. "

        docids = self.env.context.get("res_ids", False)
        sourceobj = self.env.context.get("bg_source", False)

        backgroungImg = None
        company = self._context.get("bg_company")
        company_bg_img = (company.pdf_background_image)

        if docids and sourceobj:
            source_bg_img = (sourceobj.pdf_background_image)
            if source_bg_img:
                backgroungImg = b64decode(source_bg_img)

        if not backgroungImg and company_bg_img:
            backgroungImg = b64decode(company_bg_img)

        return backgroungImg

    #Overridden:
    @api.model
    def _run_wkhtmltopdf(self, bodies, header=None, footer=None, landscape=False, specific_paperformat_args=None,
                         set_viewport_size=False,):

        result = self._prepare_pdf_content(
            bodies,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        backgroungImg = self._get_background_image()

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

