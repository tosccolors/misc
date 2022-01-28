# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrDepartment(models.Model):
    _name = 'hr.department'
    _inherit = ['hr.department', 'data.track.thread']