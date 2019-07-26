
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
        res = super(ActivityLog, self).action_log()
        note = ''
        stage_id = self.env['crm.stage'].search([('name','=','Logged')],limit=1)
        if self.note and self.note != '<p><br></p>':
            note = (BeautifulSoup(self.note, 'lxml')).get_text()
        if 'activity_from_partner' in self.env.context:
            dic = {
                'partner_id':self.partner_id and self.partner_id.id,
                'partner_contact_id':self.partner_contact_id and self.partner_contact_id.id,
                'email':self.email,
                'phone':self.phone,
                'mobile':self.mobile,
                'user_id':self.user_id and self.user_id.id,
                'description':note,
                
            }
            if not context.get('ctx_scheduled_log',False):
                dic.update({'stage_id': stage_id.id})
            if self.title_action:
                dic['name'] = "Internal Note"
            self.lead_id.write(dic)
        if not context.get('ctx_scheduled_log',False):
            self.lead_id.write({'stage_id': stage_id.id})
        return res

