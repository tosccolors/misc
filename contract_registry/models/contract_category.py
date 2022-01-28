# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ContractCategory(models.Model):
     _name = 'contract.category'
     
     name = fields.Char(
     )
     