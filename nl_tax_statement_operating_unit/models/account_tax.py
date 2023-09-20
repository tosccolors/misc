# -*- coding: utf-8 -*-
# © 2016 Lorenzo Battistini - Agile Business Group
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api, _


class AccountTax(models.Model):
    _inherit = 'account.tax'


    def get_context_values(self):
        '''
            Inherited to capture operating unit from get_context_values()
        '''
        context = self.env.context
        return (
            context.get('from_date', fields.Date.context_today(self)),
            context.get('to_date', fields.Date.context_today(self)),
            context.get('company_id', self.env.user.company_id.id),
            context.get('target_move', 'posted'),
            context.get('operating_unit_id', False)
        )

    def _account_tax_ids_with_moves(self):
        """
        Inherited to capture operating unit from get_context_values()
        else execute query without operating_unit

        """

        from_date, to_date, company_id, target_move, operating_unit = self.get_context_values()
        if operating_unit:
            req = """
                    SELECT id
                    FROM account_tax at
                    WHERE
                    company_id = %s AND
                    EXISTS (
                      SELECT 1 FROM account_move_Line aml
                      WHERE
                        date >= %s AND
                        date <= %s AND
                        operating_unit_id = %s AND
                        company_id = %s AND (
                          tax_line_id = at.id OR
                          EXISTS (
                            SELECT 1 FROM account_move_line_account_tax_rel
                            WHERE account_move_line_id = aml.id AND
                              account_tax_id = at.id
                          )
                        )
                    )
                """

            self.env.cr.execute(
                req, (company_id, from_date, to_date, operating_unit, company_id))
        else:
            req = """
                SELECT id
                FROM account_tax at
                WHERE
                company_id = %s AND
                EXISTS (
                  SELECT 1 FROM account_move_Line aml
                  WHERE
                    date >= %s AND
                    date <= %s AND
                    company_id = %s AND (
                      tax_line_id = at.id OR
                      EXISTS (
                        SELECT 1 FROM account_move_line_account_tax_rel
                        WHERE account_move_line_id = aml.id AND
                          account_tax_id = at.id
                      )
                    )
                )
            """

            self.env.cr.execute(
                req, (company_id, from_date, to_date, company_id))
        return [r[0] for r in self.env.cr.fetchall()]


    def get_move_line_partial_domain(self, from_date, to_date, company_id, operating_unit_id=False):
        domain = [
            ('date', '<=', to_date),
            ('date', '>=', from_date),
            ('company_id', '=', company_id),
        ]
        if operating_unit_id:
            domain.append(('operating_unit_id', '=', operating_unit_id))
        return domain


    def get_move_lines_domain(self, tax_or_base='tax', move_type=None):
        '''
            Inherited to capture operating unit from get_context_values()
        '''
        from_date, to_date, company_id, target_move, operating_unit = self.get_context_values()
        state_list = self.get_target_state_list(target_move)
        type_list = self.get_target_type_list(move_type)
        domain = self.get_move_line_partial_domain(
            from_date, to_date, company_id, operating_unit)
        balance_domain = []
        if tax_or_base == 'tax':
            balance_domain = self.get_balance_domain(state_list, type_list)
        elif tax_or_base == 'base':
            balance_domain = self.get_base_balance_domain(
                state_list, type_list)
        domain.extend(balance_domain)
        return domain
