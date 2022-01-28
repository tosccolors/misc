# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from openerp.tools.translate import _

class ContractPeriod(models.Model):
     _name = 'contract.period'
     
     date_start = fields.Date(string='Start Date'
     )
     date_end = fields.Date(string='End Date'
     )
     
     period_id = fields.Many2one("contract.registry",string="Period")
     
     @api.multi
     @api.constrains('date_end', 'date_start')
     def date_constrains(self):
         for rec in self:
             if rec.date_end < rec.date_start:
                 raise ValidationError(_('Sorry, End Date Must be greater Than Start Date...'))
     
     