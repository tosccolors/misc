from odoo import models, fields

class  ResCompany(models.Model):
    _inherit = 'res.company'

    reversal_via_sql = fields.Boolean(string="Reversal Via Sql", default=False)
    perform_reversal_by_line_jq = fields.Boolean(string="Perform Reversal by Line Job Queue", default=False)