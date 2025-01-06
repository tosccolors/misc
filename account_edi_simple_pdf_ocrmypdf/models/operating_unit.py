# Copyright (c) 2015 Magnus 

from odoo import api, fields, models, tools, _

class OperatingUnit(models.Model):
    _inherit = 'operating.unit'


    logo = fields.Binary(related='partner_id.image_1920')
    report_background_image1 = fields.Binary(
        'Background Image for Report Frontpage', attachment=True,
        help='Set Background Image for Report Frontpage',
    )
