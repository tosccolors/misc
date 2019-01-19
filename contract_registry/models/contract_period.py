# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractPeriod(models.Model):
     _name = 'contract.period'
     
     date_start = fields.Date(string='Start Date'
     )
     date_end = fields.Date(string='End Date'
     )
     
     period_id = fields.Many2one("contract.registry",string="Period")