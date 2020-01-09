
from odoo import models, fields, api, tools, _
from bs4 import BeautifulSoup


class ActivityLog(models.TransientModel):
    _inherit = "crm.activity.log"

    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_contact_id = fields.Many2one('res.partner', string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    user_id = fields.Many2one('res.users', string='Salesperson')
    date_action = fields.Datetime('Next Activity Date', index=True)
    
    @api.multi
    def action_log_and_schedule(self):
        self.ensure_one()
        context = dict(self._context or {})
        context.update({'ctx_scheduled_log':True})
        self.with_context(context).action_log()
        view_id = self.env.ref('crm.crm_activity_log_view_form_schedule')
        return {
            'name': _('Next activity'),
            'res_model': 'crm.activity.log',
            'context': {
                'default_last_activity_id': self.next_activity_id.id,
                'default_lead_id': self.lead_id.id
            },
            'type': 'ir.actions.act_window',
            'view_id': False,
            'views': [(view_id.id, 'form')],
            'view_mode': 'form',
            'target': 'new',
            'view_type': 'form',
            'res_id': False
        }
        
    @api.multi
    def action_log(self):
        context = dict(self._context or {})
        self = self.with_context(get_sizes=True)
        stage_id = self.env['crm.stage'].search([('name','=','Logged')],limit=1)
        stage_logged = self.env.ref("sale_advertising_order.stage_logged")
        for log in self:
            body_html = "<div><b>%(title)s</b>: %(next_activity)s</div>%(description)s%(note)s" % {
                'title': _('Activity Done'),
                'next_activity': log.next_activity_id.name,
                'description': log.title_action and '<p><em>%s</em></p>' % log.title_action or '',
                'note': log.note or '',
            }
            summary = ""
            if log.title_action: summary = log.title_action
            if log.note and log.note != '<p><br></p>':
                note = (BeautifulSoup(log.note, 'lxml')).get_text()
                if 'activity_from_partner' in self.env.context:
                    dic = {
                        'partner_id':log.partner_id and log.partner_id.id,
                        'partner_contact_id':log.partner_contact_id and log.partner_contact_id.id,
                        'email':log.email,
                        'phone':log.phone,
                        'mobile':log.mobile,
                        'user_id':log.user_id and log.user_id.id,
                        'description':note,
                        
                    }
                    if not context.get('ctx_scheduled_log',False):
                        dic.update({'stage_id': stage_id.id})
                    if self.title_action:
                        dic['name'] = "Internal Note"
                    log.lead_id.write(dic)
            if not context.get('ctx_scheduled_log',False):
                log.lead_id.write({'stage_id': stage_id.id})
            log.lead_id.message_post(body_html, subject=summary, subtype_id=log.next_activity_id.subtype_id.id)
            log.lead_id.write({
                'date_deadline': log.date_deadline,
                'planned_revenue': log.planned_revenue,
                'title_action': False,
                # 'description':note,
            })
            if log.lead_id.is_activity: log.lead_id.write({'stage_id': stage_logged.id})
        return True

    @api.multi
    def action_save(self):
        note = ''
        if self.note and self.note != '<p><br></p>':
            note = (BeautifulSoup(self.note, 'lxml')).get_text()
        dic = {
            'name': "Internal Note",
            'partner_id': self.partner_id and self.partner_id.id,
            'partner_contact_id': self.partner_contact_id and self.partner_contact_id.id,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'user_id': self.user_id and self.user_id.id,
            'description': note,
            'next_activity_id':self.next_activity_id.id,
            'date_action':self.date_deadline,
            'is_activity':True,
        }
        self.lead_id.write(dic)
        return True