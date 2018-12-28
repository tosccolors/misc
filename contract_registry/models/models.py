# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractRegistry(models.Model):
     _name = 'contract.registry'

     name = fields.Char(
     )
     operating_unit_id = fields.Many2one(
         'operating.unit',
         string="Operating Unit"
     )
     company_id = fields.many2one(
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

     @api.depends('value')
     def _value_pc(self):
         self.value2 = float(self.value) / 100