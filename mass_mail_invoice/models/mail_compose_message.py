# -*- coding: utf-8 -*-
from odoo import _, api, fields, models, SUPERUSER_ID, tools
from datetime import date
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError

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
        if not ('invoice_mass_mail' in ctx and ctx['invoice_mass_mail'] == True):
            return super(MailComposer, self).send_mail()
        else:
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
            if len(mail_inv_ids) >= 1:
                self.with_delay(description='mass_mail_invoice')._split_jobs(mail_inv_ids)
            if download_inv_ids:
                res = self.env['report'].get_action(download_inv_ids, 'account.report_invoice')

        return res

    @job
    def _split_jobs(self, inv_ids):
        size = 50
#        size = self.chunk_size
#        eta = fields.Datetime.from_string(self.execution_datetime)
        for x in xrange(0, len(inv_ids), size):
            chunk = inv_ids[x:x + size]
            self.with_delay().send_mail_job_queue(chunk)

    @job
    def send_mail_job_queue(self, mail_inv_ids):
        ctx = self.env.context.copy()
        ctx.update({'active_ids': mail_inv_ids}), ctx.update({'active_id': mail_inv_ids[0]})
        self.with_context(ctx).send_mail(False)
