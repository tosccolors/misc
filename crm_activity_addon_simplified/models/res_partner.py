# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def create_activity(self):
        crm = self.env['crm.lead']

        def _create_lead(self):
            dic = {
                'subject': "Internal Note",
                'name': "Internal Note",
                'internal_note': True,
                'type': 'opportunity',
                'partner_id':self.parent_id and self.parent_id.id or self.id,
                'partner_contact_id':not self.parent_id and self.id,
                'email':self.email,
                'phone':self.phone,
                'mobile':self.mobile,
                'user_id':self.env.uid or False,
                'is_partner_log':True,
            }
            return crm.create(dic).id

        activity_form = self.env.ref('crm_activity_addon.crm_activity_log_view_form_misc', False)
        ctx = dict(
            activity_from_partner=True,
            default_partner_id=self.parent_id and self.parent_id.id or self.id,
            default_email=self.email,
            default_phone=self.phone,
            default_mobile=self.mobile,
            default_user_id=self.env.uid or False,
            default_lead_id=_create_lead(self),
            default_is_partner_log=True
        )

        return {
            'name': _('Log'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'crm.activity.log',
            'views': [(activity_form.id, 'form')],
            'view_id': activity_form.id,
            'target': 'new',
            'context': ctx,
        }
