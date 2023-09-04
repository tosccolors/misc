
from odoo import models, fields, api, tools, _
from bs4 import BeautifulSoup


class ActivityLog(models.TransientModel):
    _inherit = "crm.activity.log"

    is_partner_log = fields.Boolean('Is Partner Log?')

    @api.multi
    def action_log(self):
        context = dict(self._context or {})
        super(ActivityLog, self).action_log()
        for log in self:
            if context.get('default_is_partner_log', False):
                log.lead_id.write({'is_partner_log': context.get('default_is_partner_log', False)})
        return True

    @api.multi
    def action_save(self):
        res = super(ActivityLog, self).action_save()
        self.lead_id.write({'is_partner_log':True})
        return res