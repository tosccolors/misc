from odoo import models, fields

class  ResCompany(models.Model):
    _inherit = 'res.company'

    reversal_via_sql = fields.Boolean(string="Reversal Via Sql", default=False)