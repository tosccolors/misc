# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields,_

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    segment_one = fields.Many2one("segment.one","Segment 1")
    segment_two = fields.Many2one("segment.two","Segment 2")
    segment_three = fields.Many2one("segment.three","Segment 3")
    segment_four = fields.Many2one("segment.four","Segment 4")
    
    