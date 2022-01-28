# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields,_

class SegmentOne(models.Model):
    _name = 'segment.one'
    
    name = fields.Char("Segment Name")
    
class SegmentTwo(models.Model):
    _name = 'segment.two'
    
    name = fields.Char("Segment Name")
    
class SegmentThree(models.Model):
    _name = 'segment.three'
    
    name = fields.Char("Segment Name")
    
class SegmentFour(models.Model):
    _name = 'segment.four'
    
    name = fields.Char("Segment Name")
    