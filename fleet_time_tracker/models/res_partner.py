# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'data.track.thread']