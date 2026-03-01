from odoo import fields, models


class AccountReconcileModel(models.Model):
    _inherit = 'account.reconcile.model'

    extra_statement_text_delimiters = fields.Char(
        'Token delimiters',
        help='Fill in extra charaters used as token delimiters for splitting the above fields',
    )

    def _get_st_line_text_values_for_matching(self, st_line):
        result = super()._get_st_line_text_values_for_matching(st_line)
        for i in range(len(result)):
            for delimiter in (self.extra_statement_text_delimiters or []):
                result[i] = result[i].replace(delimiter, ' ')
        return result
