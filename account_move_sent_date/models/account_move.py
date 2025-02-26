from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    sent_date = fields.Date()

    def write(self, vals):
        if vals.get('is_move_sent') and 'sent_date' not in vals:
            vals['sent_date'] = fields.Date.today()
        return super().write(vals)
