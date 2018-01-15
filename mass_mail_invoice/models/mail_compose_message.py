# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, SUPERUSER_ID, tools

class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        result = super(MailComposer, self).default_get(fields)
        if 'invoice_mass_mail' in self._context:
            result.update({'use_active_domain':False})
            result['res_id'] = False
        return result

    @api.multi
    def send_mail(self, auto_commit=False):
        ctx = self.env.context.copy()
        if 'invoice_mass_mail' in ctx and ctx['invoice_mass_mail'] == True:
            inv_ids = []
            if 'active_model' in ctx and ctx['active_model'] == 'account.invoice':
                for invoice_obj in self.env['account.invoice'].browse(ctx['active_ids']):
                    if invoice_obj.partner_id.transmit_invoice == 'email':
                        inv_ids.append(invoice_obj.id)
                        self.res_id = inv_ids[0]
            ctx.update({'active_ids':inv_ids}),ctx.update({'active_id':inv_ids[0]}) if inv_ids else ctx
        return super(MailComposer, self.with_context(ctx)).send_mail()

MailComposer()