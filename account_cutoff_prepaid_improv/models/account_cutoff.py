# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    def get_prepaid_lines(self):
        self.ensure_one()
        if not self.source_journal_ids:
            raise UserError(
                _("You should set at least one Source Journal."))
        cutoff_date_str = self.cutoff_date
        # Delete existing lines
        query = ("""DELETE FROM account_cutoff_line
                    WHERE parent_id = %s;
        """)
        self.env.cr.execute(query, [self.id])
        sql_query = ("""
                    INSERT into account_cutoff_line (
                                                    parent_id, 
                                                    move_line_id, 
                                                    partner_id, 
                                                    name, 
                                                    start_date,
                                                    end_date, 
                                                    account_id, 
                                                    cutoff_account_id, 
                                                    analytic_account_id,
                                                    total_days, 
                                                    prepaid_days, 
                                                    amount, 
                                                    currency_id, 
                                                    cutoff_amount,
                                                    create_uid,
                                                    create_date,
                                                    write_uid,
                                                    write_date
                                                    )
                    SELECT {0} AS parent_id,
                            l.id AS move_line_id, 
                            l.partner_id AS partner_id, 
                            l.name AS name, 
                            l.start_date AS start_date, 
                            l.end_date AS end_date, 
                            l.account_id AS account_id, 
                            CASE
                              WHEN (a.cutoff_account_id IS NULL OR a.cutoff_account_id = '') THEN l.account_id
                              ELSE a.cutoff_account_id
                            END AS cutoff_account_id,
                            l.analytic_account_id AS analytic_account_id, 
                            l.end_date - l.start_date + 1 AS total_days,
                            CASE
                              {1}
                            END AS prepaid_days,
                            l.credit - l.debit AS amount, 
                            {2} AS currency_id, 
                            (l.debit - l.credit) * prepaid_days / total_days AS cutoff_amount,
                            {5} as create_uid,
                            {6} as create_date,
                            {5} as write_uid,
                            {6} as write_date
                    FROM           
                            account_move_line l
                                    LEFT JOIN account_cutoff_mapping a ON (a.account_id = l.account_id)
                    WHERE {3}{4};                
        """.format(self.id,
                   'WHEN l.start_date > %s THEN total_days ELSE l.end_date - %s' % self.cutoff_date if not self.forecast
                   else 'WHEN l.start_date < %s AND l.end_date > %s THEN total_days - (%s - start_date) - (end_date - %s) '
                        'WHEN l.start_date > %s AND l.end_date > %s THEN total_days - (end_date - %s) '
                        'WHEN l.start_date > %s AND l.end_date < %s THEN total_days'
                        % (self.start_date, self.end_date, self.start_date, self.end_date, self.start_date, self.end_date, self.end_date,
                           self.start_date, self.end_date),
                   self.company_currency_id.id,
                   "l.start_date != %s "
                   "AND l.journal_id in %s "
                   "AND l.end_date > %s "
                   "AND l.date <= %s" % (False, self.source_journal_ids.ids, cutoff_date_str, cutoff_date_str) if not self.forecast
                   else
                    "l.start_date <= %s "
                    "AND l.journal_id in %s "
                    "AND l.end_date >= %s " % (self.end_date, self.source_journal_ids.ids, self.start_date),
                    "AND a.company_id = %s AND a.cutoff_type = %s" % (self.company_id.id, self.type),
                   self._uid,
                   str(fields.Datetime.to_string(fields.datetime.now()))

                   ))
        self.env.cr.execute(query, locals())
        return True

