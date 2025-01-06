from odoo import fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    migration_remarks = fields.Text(string='Migration Remarks', help='Remarks for migration purposes')
