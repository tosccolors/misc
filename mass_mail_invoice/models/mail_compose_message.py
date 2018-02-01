# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, SUPERUSER_ID, tools
from datetime import date

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
        res = {}
        if 'invoice_mass_mail' in ctx and ctx['invoice_mass_mail'] == True:
            mail_inv_ids = []
            download_inv_ids = []
            user_obj = self.env.user
            res = {'type': 'ir.actions.act_window_close'} # by default close wizard will be called.
            if 'active_model' in ctx and ctx['active_model'] == 'account.invoice':
                for invoice_obj in self.env['account.invoice'].browse(ctx['active_ids']):
                    if invoice_obj.transmit_method_code:
                        transmit_code = invoice_obj.transmit_method_code.strip().lower()
                        invoice_obj.sent_date = date.today()
                        if transmit_code == 'post' and user_obj.printing_action:
                            if user_obj.printing_action == 'client':
                                download_inv_ids.append(invoice_obj.id)
                            elif user_obj.printing_action == 'server':
                                self.env['report'].print_document(record_ids=[invoice_obj.id], report_name='account.report_invoice', html=None, data=None)
                        elif transmit_code == 'mail':
                            mail_inv_ids.append(invoice_obj.id)
            if mail_inv_ids:
                ctx.update({'active_ids':mail_inv_ids}),ctx.update({'active_id':mail_inv_ids[0]})
                res = super(MailComposer, self.with_context(ctx)).send_mail()

            if download_inv_ids:
                ctx.update({'active_ids':download_inv_ids})
                res = {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'account.report_invoice',
                    'context': ctx
                  }
        return res

MailComposer()