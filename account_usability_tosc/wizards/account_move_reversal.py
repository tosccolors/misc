from odoo import api, fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    @api.model
    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        if 'date' in result:
            result['date'] = fields.Date.today()
        return result
