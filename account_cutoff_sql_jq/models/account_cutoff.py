# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError


class AccountCutoff(models.Model):
    _inherit = 'account.cutoff'

    job_queue = fields.Many2one(
        'queue.job', string='Job Queue', readonly=True,
        copy=False)

    def _prepare_provision_line(self, cutoff_line):
        result = super(AccountCutoff, self)._prepare_provision_line(cutoff_line)
        result['account_move_ref'] = cutoff_line.invoice_id.number
        result['account_move_label'] = cutoff_line.move_line_id.display_name if not \
            self.env.user.company_id.use_description_as_reference else \
                cutoff_line.name
        return result

    def _merge_provision_lines(self, provision_lines):
        return provision_lines

    def _prepare_move(self, to_provision):
        self.ensure_one()
        movelines_to_create = []
        ref = self.move_label or ''
        for dict in to_provision:
            amount = dict['amount']
            analytic_account_id = dict['analytic_account_id']
            operating_unit_id = dict['operating_unit_id']
            account_id = dict['account_id']
            move_label = dict['account_move_label']
            move_ref = ref + " " + dict.get('account_move_ref', '') or ''
            amount = self.company_currency_id.round(amount)
            movelines_to_create.append((0, 0, {
                'account_id': account_id,
                'name': move_label,
                'ref': move_ref,
                'debit': amount < 0 and amount * -1 or 0,
                'credit': amount >= 0 and amount or 0,
                'analytic_account_id': analytic_account_id,
                'operating_unit_id': operating_unit_id
            }))

            # add counter-part
            counterpart_amount = self.company_currency_id.round(
                amount * -1)
            movelines_to_create.append((0, 0, {
                'account_id': self.cutoff_account_id.id,
                'name': move_label,
                'ref': move_ref,
                'debit': counterpart_amount < 0 and counterpart_amount * -1 or 0,
                'credit': counterpart_amount >= 0 and counterpart_amount or 0,
                'analytic_account_id': False,
                'operating_unit_id': operating_unit_id
            }))

        res = {
            'journal_id': self.cutoff_journal_id.id,
            'date': self.cutoff_date,
            'to_be_reversed': True,
            'line_ids': movelines_to_create,
        }
        return res

    def _create_move_and_line_with_query(self, vals):
        # Create move
        type = self._context.get('default_type')
        move_type = False
        if type in ['prepaid_revenue', 'accrued_revenue']:
            move_type = "receivable_refund"
        if type in ['prepaid_expense','accrued_expense']:
            move_type = "payable"

        vals.update({'name': "/",
                     'state': "draft",
                     'create_date': datetime.now(),
                     'create_uid': self._uid,
                     'write_date': datetime.now(),
                     'write_uid': self._uid,
                     'company_id': self.env.user.company_id.id,
                     'currency_id': self.env.user.company_id.currency_id and self.env.user.company_id.currency_id.id,
                     'matched_percentage': 0.0,
                     'to_be_reversed': True,
                     'move_type': move_type
                     })

        cr = self._cr
        sql = "INSERT INTO account_move (ref, date, journal_id, name, state, create_date, create_uid, write_date, write_uid," \
              " company_id, currency_id, matched_percentage, to_be_reversed, move_type) " \
              "VALUES ('%(ref)s', '%(date)s'::date, %(journal_id)s, '%(name)s', '%(state)s', '%(create_date)s', %(create_uid)s, '%(write_date)s', %(write_uid)s," \
              " %(company_id)s, %(currency_id)s, %(matched_percentage)s, %(to_be_reversed)s, '%(move_type)s');" % vals
        cr.execute(sql)
        sql = 'select id from account_move order by id desc limit 1'
        cr.execute(sql)
        move_id = cr.fetchone()[0]
        account_move = self.env['account.move'].browse([move_id])[0]
        journal_id = account_move.journal_id.id

        # Create move line
        sql_query = ("""
                    INSERT INTO account_move_line (
                                                    account_id,
                                                    move_id,
                                                    date_maturity,
                                                    name,
                                                    debit,
                                                    credit,
                                                    journal_id,
                                                    create_uid,
                                                    create_date,
                                                    write_uid,
                                                    write_date,
                                                    ref,
                                                    company_currency_id,
                                                    amount_currency,
                                                    amount_residual,
                                                    analytic_account_id,
                                                    operating_unit_id,
                                                    balance,
                                                    debit_cash_basis,
                                                    credit_cash_basis,
                                                    balance_cash_basis,
                                                    blocked,
                                                    company_id,
                                                    date,
                                                    user_type_id
                                                    )
                    SELECT
                            cl.account_id AS account_id,
                            {0} AS move_id,
                            {1} AS date_maturity,
                            CASE
                                WHEN {9} THEN cl.name
                                ELSE CONCAT({5}, m.name)
                            END AS name,
                            CASE
                              WHEN cl.cutoff_amount < 0 THEN ROUND(cl.cutoff_amount * -1, 2)
                              ELSE 0.0
                            END AS debit,
                            CASE
                              WHEN cl.cutoff_amount > 0 THEN ROUND(cl.cutoff_amount, 2)
                              ELSE 0.0
                            END AS credit,
                            {4} AS journal_id,
                            {2} as create_uid,
                            {3} as create_date,
                            {2} as write_uid,
                            {3} as write_date,
                            CONCAT({5}, m.name) AS ref,
                            {6} AS company_currency_id,
                            0.0 AS amount_currency,
                            ROUND(cl.cutoff_amount * -1, 2) AS amount_residual,
                            cl.analytic_account_id AS analytic_account_id,
                            cl.operating_unit_id AS operating_unit_id,
                            ROUND(cl.cutoff_amount * -1, 2) AS balance,
                            CASE
                              WHEN cl.cutoff_amount < 0 THEN ROUND(cl.cutoff_amount * -1, 2)
                              ELSE 0.0
                            END AS debit_cash_basis,
                            CASE
                              WHEN cl.cutoff_amount > 0 THEN ROUND(cl.cutoff_amount, 2)
                              ELSE 0.0
                            END AS credit_cash_basis,
                            ROUND(cl.cutoff_amount * -1, 2) AS balance_cash_basis,
                            FALSE AS blocked,
                            {7} AS company_id,
                            {1} AS date,
                            aa.user_type_id AS user_type_id

                    FROM account_cutoff_line cl
                    LEFT JOIN account_account aa ON (cl.account_id = aa.id)
                    LEFT JOIN account_move_line ml ON (ml.id = cl.move_line_id)
                    LEFT JOIN account_move m ON (m.id = ml.move_id)
                    WHERE parent_id = {8}
                    AND cl.cutoff_amount is not 0;
        """.format(move_id,
                   "'%s'" % str(account_move.date),
                   self._uid,
                   "'%s'" % str(fields.Datetime.to_string(fields.datetime.now())),
                   journal_id,
                   "'%s '" % self.move_label,
                   self.company_currency_id.id,
                   self.env.user.company_id.id,
                   self.id,
                   self.env.user.company_id.use_description_as_reference
                   ))
        cr.execute(sql_query)

        # Add counter-part
        sql_query = ("""
                    INSERT INTO account_move_line (
                            create_date,
                            statement_id,
                            journal_id,
                            currency_id,
                            date_maturity,
                            user_type_id,
                            partner_id,
                            blocked,
                            analytic_account_id,
                            operating_unit_id,
                            create_uid,
                            amount_residual,
                            company_id,
                            credit_cash_basis,
                            amount_residual_currency,
                            debit,
                            ref,
                            account_id,
                            debit_cash_basis,
                            tax_exigible,
                            balance_cash_basis,
                            write_date,
                            date,
                            write_uid,
                            move_id,
                            company_currency_id,
                            name,
                            credit,
                            amount_currency,
                            balance,
                            quantity
                            )
                    SELECT
                            create_date,
                            statement_id,
                            journal_id,
                            currency_id,
                            date_maturity,
                            {2} AS user_type_id,
                            partner_id,
                            blocked,
                            NULL AS analytic_account_id,
                            operating_unit_id,
                            create_uid,
                            amount_residual * -1 AS amount_residual,
                            company_id,
                            debit_cash_basis AS credit_cash_basis,
                            amount_residual_currency,
                            credit AS debit,
                            ref,
                            {0} AS account_id,
                            credit_cash_basis AS debit_cash_basis,
                            tax_exigible,
                            balance_cash_basis * -1 AS balance_cash_basis,
                            write_date,
                            date,
                            write_uid,
                            move_id,
                            company_currency_id,
                            name,
                            debit AS credit,
                            amount_currency,
                            balance * -1 AS balance,
                            quantity

                    FROM account_move_line
                    WHERE move_id = {1};
        """.format(
            self.cutoff_account_id.id,
            move_id,
            self.cutoff_account_id.user_type_id.id,
        ))
        cr.execute(sql_query)
        return move_id

    def create_move(self):
        self.ensure_one()
        move_obj = self.env['account.move']
        if self.move_id:
            raise UserError(_(
                "The Cut-off Journal Entry already exists. You should "
                "delete it before running this function."))
        if not self.line_ids:
            raise UserError(_(
                "There are no lines on this Cut-off, so we can't create "
                "a Journal Entry."))
        provision_lines = []
        for line in self.line_ids:
            provision_lines.append(
                self._prepare_provision_line(line))
            for tax_line in line.tax_line_ids:
                provision_lines.append(
                    self._prepare_provision_tax_line(tax_line))
        to_provision = self._merge_provision_lines(provision_lines)
        vals = self._prepare_move(to_provision)

        if self.env.user.company_id.perform_posting_by_line:
            # Create account move and lines using sql query
            move_id = self._create_move_and_line_with_query(vals)
            self.write({'move_id': move_id, 'state': 'done'})

            action = self.env['ir.actions.act_window'].for_xml_id(
                'account', 'action_move_journal_line')
            action.update({
                'view_mode': 'form,tree',
                'res_id': move_id,
                'view_id': False,
                'views': False,
            })
            return action

        elif self.env.user.company_id.perform_posting_by_line_jq:
            # Create account move and lines using job queue
            jq = self.with_delay(eta=datetime.now(), priority=1,
                                 description="Create Move By Job Queues", ).create_move_job_queue(vals)
            job_id = self.env['queue.job'].search([('uuid', '=', jq.uuid)])
            self.job_queue = job_id.id
        else:
            # Create account move and lines using ORM
            acc_move = move_obj.create(vals)
            move_id = acc_move.id
            acc_move.post()
            self.write({'move_id': move_id, 'state': 'done'})
            action = self.env['ir.actions.act_window'].for_xml_id(
                'account', 'action_move_journal_line')
            action.update({
                'view_mode': 'form,tree',
                'res_id': move_id,
                'view_id': False,
                'views': False,
            })
            return action

    # Create account move and lines using job queue
    @job
    def create_move_job_queue(self, vals):
        move_obj = self.env['account.move']
        try:
            acc_move = move_obj.create(vals)
            move_id=acc_move.id
            acc_move.post()
            self.write({'move_id': move_id, 'state': 'done'})
        except Exception, e:
            raise FailedJobError(
                _("The details of the error:'%s'") % (unicode(e)))

    def remove_zero_lines(self):
        noamt_lines = self.line_ids.filtered(lambda l: not l.amount)
        noamt_lines.unlink()
        return

    def get_lines_sql(self):
        self.ensure_one()
        if not self.source_journal_ids:
            raise UserError(
                _("You should set at least one Source Journal!"))
        cutoff_date_str = str(self.cutoff_date)
        sj_ids = self.source_journal_ids.ids
        str_lst = ','.join([str(item) for item in sj_ids])
        cutoff_id = self.id
        # Delete existing lines
        query = ("""DELETE FROM account_cutoff_line
                    WHERE parent_id = %s;""")
        self.env.cr.execute(query, [cutoff_id])

        if self.forecast:
            start_date_str = str(self.start_date)
            end_date_str = str(self.end_date)
            vara = "WHEN l.start_date < '%s' AND l.end_date > '%s' " \
                   "THEN l.end_date - l.start_date + 1 - ('%s' - start_date) - (end_date - '%s') " \
                   "WHEN l.start_date > '%s' AND l.end_date > '%s' " \
                   "THEN l.end_date - l.start_date + 1 - (end_date - '%s') " \
                   "WHEN l.start_date > '%s' AND l.end_date < '%s' " \
                   "THEN l.end_date - l.start_date + 1 " % (
                       start_date_str, end_date_str, start_date_str, end_date_str, start_date_str, end_date_str,
                       end_date_str,
                       start_date_str, end_date_str)
            varb = "l.start_date <= '%s' AND l.journal_id IN (%s) AND l.end_date >= '%s' " % (
                end_date_str, str_lst, start_date_str)

        elif self.type in ['prepaid_expense', 'prepaid_revenue']:
            vara = "WHEN l.start_date > '%s' " \
                   "THEN l.end_date - l.start_date + 1 ELSE l.end_date - '%s'" % (cutoff_date_str, cutoff_date_str)
            varb = "l.start_date IS NOT NULL AND l.journal_id IN (%s) AND l.end_date > '%s' AND l.date <= '%s' " % (
                str_lst, cutoff_date_str, cutoff_date_str)

        elif self.type in ['accrued_expense', 'accrued_revenue']:
            vara = "WHEN l.end_date <= '%s' " \
                   "THEN l.end_date - l.start_date + 1 ELSE '%s' - l.start_date" % (cutoff_date_str, cutoff_date_str)
            varb = "l.start_date IS NOT NULL AND l.journal_id IN (%s) AND l.start_date <= '%s' AND l.date > '%s' " % (
                str_lst, cutoff_date_str, cutoff_date_str)

        sql_query = ("""
                    INSERT INTO account_cutoff_line (
                                                    parent_id, 
                                                    move_line_id, 
                                                    partner_id, 
                                                    name, 
                                                    start_date,
                                                    end_date, 
                                                    account_id, 
                                                    cutoff_account_id, 
                                                    analytic_account_id,
                                                    operating_unit_id,
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
                              WHEN a.cutoff_account_id IS NULL THEN l.account_id
                              ELSE a.cutoff_account_id
                            END AS cutoff_account_id,
                            l.analytic_account_id AS analytic_account_id,
                            l.operating_unit_id AS operating_unit_id,
                            l.end_date - l.start_date + 1 AS total_days,
                            CASE
                              {1}
                            END AS prepaid_days,
                            l.credit - l.debit AS amount, 
                            {2} AS currency_id, 
                            (l.debit - l.credit) * (CASE {1} END) / (l.end_date - l.start_date + 1) AS cutoff_amount,
                            {5} as create_uid,
                            {6} as create_date,
                            {5} as write_uid,
                            {6} as write_date


                    FROM    account_move_line l LEFT JOIN account_cutoff_mapping a 
                    ON (l.account_id = a.account_id {4})
                    WHERE {3};                
        """.format(cutoff_id,
                   vara,
                   self.company_currency_id.id,
                   varb,
                   "AND a.company_id = %s AND a.cutoff_type = '%s'" % (self.company_id.id, str(self.type)),
                   self._uid,
                   "'%s'" % str(fields.Datetime.to_string(fields.datetime.now()))
                   ))
        self.env.cr.execute(sql_query)
        self.remove_zero_lines()
        return True

    def get_lines(self):
        res = super(AccountCutoff, self).get_lines()
        self.remove_zero_lines()
        return res
