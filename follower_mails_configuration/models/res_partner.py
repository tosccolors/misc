# -*- coding: utf-8 -*-

from odoo import api, fields, exceptions, models, _

class Partner(models.Model):
    _inherit = 'res.partner'
    
    #partner linked with users should be marked as customer
    @api.model
    def create(self, values):
        res = super(Partner, self).create(values)
        ctx = self.env.context.copy()
        if res.user_ids:
            ctx.update({'falseCustomer':False})
            res.with_context(ctx).write({'customer':False})
        return res

    
    def write(self, values):
        res = super(Partner, self).write(values)
        ctx = self.env.context.copy()
        if 'falseCustomer' in self.env.context:
            return res
        for partner in self:
            if partner.user_ids:
                ctx.update({'falseCustomer': False})
                partner.with_context(ctx).write({'customer': False})
        return res
