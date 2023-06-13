# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Company(models.Model):
    _inherit = "res.company"

    pdf_background_image = fields.Binary("Background Image Pdf", help="Upload a background image in Pdf format.")

