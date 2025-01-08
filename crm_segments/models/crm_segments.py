# -*- coding: utf-8 -*-
#    Copyright (C) 2022-present TOSC (<http://www.tosc.nl>). All Rights Reserved

from odoo import api, models, fields,_

class SegmentOne(models.Model):
    _name = 'segment.one'
    
    name = fields.Char("Segment Name", required=True)
    sequence = fields.Integer(default=1)
    
class SegmentTwo(models.Model):
    _name = 'segment.two'
    
    name = fields.Char("Segment Name", required=True)
    sequence = fields.Integer(default=1)
    
class SegmentThree(models.Model):
    _name = 'segment.three'
    
    name = fields.Char("Segment Name", required=True)
    sequence = fields.Integer(default=1)
    
class SegmentFour(models.Model):
    _name = 'segment.four'
    
    name = fields.Char("Segment Name", required=True)
    sequence = fields.Integer(default=1)
    