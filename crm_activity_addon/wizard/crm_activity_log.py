
from odoo import models, fields, api, tools, _
# from odoo.tools import html2text, ustr
from bs4 import BeautifulSoup


class ActivityLog(models.TransientModel):
    _inherit = "crm.activity.log"

    partner_id = fields.Many2one('res.partner', string='Customer')
    partner_contact_id = fields.Many2one('res.partner', string='Contact Person')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    user_id = fields.Many2one('res.users', string='Salesperson')

    @api.multi
    def action_log(self):
        res = super(ActivityLog, self).action_log()
        note = ''
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
            if self.title_action:
                dic['name'] = self.title_action
            self.lead_id.write(dic)

        return res



