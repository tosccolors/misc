# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractRegistry(models.Model):
     _name = 'contract.registry'

     
     state = fields.Selection([
            ('draft', 'Draft'),
            ('renew', 'Renew'),
            ('done', 'Done'),
        ],
            'State', select=True, readonly=True, track_visibility='onchange',
            help="",default='draft'
     )
     name = fields.Char(
     )
     operating_unit_id = fields.Many2one(
         'operating.unit',
         string="Operating Unit"
     )
     company_id = fields.Many2one(
         'res.company',
         string="Company"
     )
     contract_partner_ids = fields.Many2many(
         'res.partner',
         'contract_registry_res_partner_rel',
         'contract_id',
         'partner_id',
         'Concerned Business Partners'
     )
     value = fields.Integer(

     )
     value2 = fields.Float(
         compute="_value_pc",
         store=True
     )
     description = fields.Text(

     )

     renewable = fields.Boolean('is Renewable?'
     )
     one_time = fields.Boolean('One Time'
     )
     alert_date = fields.Date("Date"
     )
     responsible_officer_id = fields.Many2one(
         'res.users',
         string="Responsible Officer"
     )
     contract_category_id = fields.Many2one(
         'contract.category',
         string="Contract Category"
     )
     period_ids = fields.One2many('contract.period', 'period_id', string='Period', copy=True
     )

     
     
     @api.depends('value')
     def _value_pc(self):
         self.value2 = float(self.value) / 100
         
     @api.multi
     def done_contract(self):
         self.write({'state':'done'})
         
     @api.multi
     def renew_contract(self):
         self.write({'state':'renew'})
         
    
