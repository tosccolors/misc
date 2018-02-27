# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class AccountAccount(models.Model):
    _inherit = "account.account"
    _description = "Account"

    operating_unit_id = fields.Many2one('operating.unit', string="Operating Unit", ondelete='restrict')

    @api.multi
    def write(self, vals):
        # Dont allow changing the operating_unit_id when account_move_line already exist
        if vals.get('operating_unit_id', False) and self.operating_unit_id:
            move_lines = self.env['account.move.line'].search([('account_id', 'in', self.ids)], limit=1)
            for account in self:
                if (account.operating_unit_id.id <> vals['operating_unit_id']) and move_lines:
                    raise UserError(_('You cannot change the operating unit of an account that already contains journal items.'))
        return super(AccountAccount, self).write(vals)
