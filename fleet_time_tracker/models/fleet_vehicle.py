# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FleetVehicle(models.Model):
    _name = 'fleet.vehicle'
    _inherit = ['fleet.vehicle', 'data.track.thread']