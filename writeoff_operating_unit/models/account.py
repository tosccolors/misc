# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def prepare_move_lines_for_reconciliation_widget(self, target_currency=False, target_date=False):
        ret = super(AccountMoveLine, self).prepare_move_lines_for_reconciliation_widget(target_currency, target_date)
        for index, ret_line in enumerate(ret):
            ret[index]['operating_unit'] = self.browse(ret_line['id']).operating_unit_id.name
        return ret