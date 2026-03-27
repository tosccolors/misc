from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartnerBank(models.Model):
   
       #Update vendor bank account with states 
    
    _inherit = 'res.partner.bank'
    
    state = fields.Selection([('draft', "Draft"),('confirmed', "Confirmed")],default='draft',string='Status', copy=False, index=True,readonly=True, store=True,track_visibility='always')
    
    def action_draft(self):
        self.state = 'draft'
    
    def action_confirm(self):
        self.state = 'confirmed'

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].browse(vals.get('partner_id') or [])
        if partner.supplier_rank:
            vals['state'] = 'draft'
        else:
            vals['state'] = 'confirmed'
        return super().create(vals)
    
    def write(self, vals):
        if any(self.mapped('partner_id.supplier_rank')) and set(vals) != set(['state']):
            vals['state'] = 'draft'
        return super().write(vals)
