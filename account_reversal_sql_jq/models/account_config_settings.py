from odoo import models, fields

class AccountConfigSettings(models.TransientModel):
    
    _inherit = 'account.config.settings'

    reversal_via_sql = fields.Boolean(string="Reversal Via Sql", related='company_id.reversal_via_sql')
    perform_reversal_by_line_jq = fields.Boolean(string="Perform Reversal by Line Job Queue with SQL", related='company_id.perform_reversal_by_line_jq')