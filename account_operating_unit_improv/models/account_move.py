# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo.tools.translate import _
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        if 'apply_taxes' in self.env.context:
            if res.tax_ids and res.operating_unit_id:
                objmove = res.move_id.line_ids.search([('tax_line_id','in',res.tax_ids.ids),('operating_unit_id','=',False)])
                objmove.write({'operating_unit_id':res.operating_unit_id.id})
            elif res.tax_line_id and not res.operating_unit_id :
                objmove = res.move_id.line_ids.search([('tax_ids', '=', res.tax_line_id.id),('operating_unit_id', '!=', False)],limit=1)
                res.write({'operating_unit_id': objmove.operating_unit_id.id})
        return res

    
    def write(self, vals):
        result = super(AccountMoveLine, self).write(vals)
        if 'operating_unit_id' in vals:
            self._update_check()
        return result

class AccountMove(models.Model):
    _inherit = "account.move"

    operating_unit_id = fields.Many2one('operating.unit',
                                        'Default operating unit', states={'posted': [('readonly', True)]},
                                        help="This operating unit will "
                                             "be defaulted in the move lines.")


    '''
    
    def post(self):
        ml_obj = self.env['account.move.line']
        for move in self:
            if not move.company_id.ou_is_self_balanced:
                continue

            # If all move lines point to the same operating unit, there's no
            # need to create a balancing move line
            # check at the same time again without any additional cost if _check_ou()
            # still holds. Only a check at write/create is a bit too thin for such a
            # sensitive matter
            ou_list_ids = []
            for line in move.line_ids:
                if line.operating_unit_id:
                    ou_list_ids.append(line.operating_unit_id and line.operating_unit_id.id)
                else:
                    raise UserError(_('Configuration error!\nDuring move posting:\nThe operating\
                                    unit must be completed for each line if the operating\
                                    unit has been defined as self-balanced at company level.'))
            if len(ou_list_ids) <= 1:
                continue

            # Create balancing entries for un-balanced OU's.
            ou_balances = self._check_ou_balance(move)
            amls = []
            for ou_id in ou_balances.keys():
                # If the OU is already balanced, then do not continue
                if move.company_id.currency_id.is_zero(ou_balances[ou_id]):
                    continue
                # Create a balancing move line in the operating unit
                # clearing account
                line_data = self._prepare_inter_ou_balancing_move_line(
                    move, ou_id, ou_balances)
                if line_data:
                    amls.append(ml_obj.with_context(wip=True).
                                create(line_data))
            if amls:
                move.with_context(wip=False).\
                    write({'line_ids': [(4, aml.id) for aml in amls]})

        return super(AccountMove, self).post()
        '''
