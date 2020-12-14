# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, models, fields,_

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    segment_one = fields.Many2one("segment.one","Segment 1",track_visibility='always')
    segment_two = fields.Many2one("segment.two","Segment 2",track_visibility='always')
    segment_three = fields.Many2one("segment.three","Segment 3",track_visibility='always')
    segment_four = fields.Many2one("segment.four","Segment 4",track_visibility='always')
    has_segments_group = fields.Boolean(string="Check Group", compute='_check_user_group', default=lambda self: self.env.user.has_group('crm_segments.group_sale_segments'))

    @api.one
    def _check_user_group(self):
        current_uid = self.env.uid
        res_users = self.env['res.users'].browse(current_uid)
        if res_users.has_group('crm_segments.group_sale_segments'):
            self.has_segments_group = True
        else:
            self.has_segments_group = False