from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    migration_remarks = fields.Text(string="Migration Remarks")