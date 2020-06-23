# coding: utf-8
# @ 2015 Florian DA COSTA @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo 
from odoo import _, api, fields, models

class FetchmailServer(models.Model):
    _inherit='fetchmail.server'
    
    operating_unit_id = fields.Many2one('operating.unit',string='Operating Unit',)
    metadata_attachment = fields.Selection([('single_metadata', 'All attachments into one Metadata attachment'), ('multiple_metadata', 'Each attachment into one Metadata attachment')], string="Create Metadata")