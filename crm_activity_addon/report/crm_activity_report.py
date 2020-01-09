# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ActivityReport(models.Model):
    """ CRM Lead Analysis """

    _inherit = "crm.activity.report"
    
    description = fields.Char('Note', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'crm_activity_report')
        self._cr.execute("""
            CREATE VIEW crm_activity_report AS (
                select
                    m.id,
                    m.subtype_id,
                    m.author_id,
                    m.date,
                    m.subject,
                    l.id as lead_id,
                    l.user_id,
                    l.team_id,
                    l.country_id,
                    l.company_id,
                    l.stage_id,
                    l.partner_id,
                    l.type as lead_type,
                    l.active,
                    l.probability,
                    regexp_replace(SPLIT_PART(m.body,'</em></p>',2), E'<[^>]+>', '', 'gi') as description
                from
                    "mail_message" m
                join
                    "crm_lead" l
                on
                    (m.res_id = l.id)
                WHERE
                    (m.model = 'crm.lead')
            )""")
