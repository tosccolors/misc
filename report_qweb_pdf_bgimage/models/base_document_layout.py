# -*- coding: utf-8 -*-

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    full_background_img = fields.Binary(
        related="company_id.pdf_background_image",
        readonly=False,
        help="Replaces whole report with image",
    )

    @api.depends(
        "full_background_img",
    )
    def _compute_preview(self):
        super()._compute_preview()
