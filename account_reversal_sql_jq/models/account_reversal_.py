# -*- coding: utf-8 -*-

from odoo import api, fields, models, exceptions, _
from datetime import date, datetime
from odoo.addons.queue_job.job import job, related_action
from odoo.addons.queue_job.exception import FailedJobError
from odoo.exceptions import UserError
from odoo.tools import exception_to_unicode


class AccountMove(models.Model):
    _inherit = "account.move"

    job_queue = fields.Many2one('queue.job', string='Job Queue', readonly=True, copy=False)

    def create_reversal_moveline_with_query(self, date, journal):

        #  Create move
        operating_unit_id = self.operating_unit_id and self.operating_unit_id.id or "NUll"
        uid = self._uid
        company = self.env.user.company_id

        journal = journal or self.journal_id
        if journal.company_id != self.company_id:
            raise UserError(
                _("Wrong company Journal is '%s' but we have '%s'") % (
                    journal.company_id.name, self.company_id.name))

        ref = self.ref
        # if move_prefix and move_prefix != ref:
        #     ref = ' '.join([move_prefix, ref])

        data = {
            'ref': ref,
            'narration': self.narration,
            'operating_unit_id': operating_unit_id,
            'date': date or self.date,
            'journal_id': journal.id,
            'name': '/',
            'state': "draft",
            'create_date': datetime.now(),
            'create_uid': uid,
            'write_date': datetime.now(),
            'write_uid': uid,
            'company_id': company.id,
            'currency_id': company.currency_id and company.currency_id.id,
            'matched_percentage': 0.0,
            'to_be_reversed': False,
            'move_type':'other'
        }

        cr = self._cr
        sql = "INSERT INTO account_move (ref,narration,operating_unit_id," \
              " date,journal_id, name, state, create_date, create_uid, write_date, write_uid," \
              " company_id, currency_id,move_type,matched_percentage, to_be_reversed) " \
              "VALUES ('%(ref)s','%(narration)s',%(operating_unit_id)s,'%(date)s'::date," \
              "%(journal_id)s,'%(name)s', '%(state)s', '%(create_date)s', %(create_uid)s, '%(write_date)s', %(write_uid)s," \
              " %(company_id)s, %(currency_id)s,'%(move_type)s',%(matched_percentage)s, %(to_be_reversed)s);" % data
        cr.execute(sql)
        sql = 'select id from account_move order by id desc limit 1'
        cr.execute(sql)
        move_id = cr.fetchone()[0]

        # Create move line       

        sql_query = ("""
                    INSERT INTO account_move_line (
                            create_date,
                            partner_bank_id,
                            partner_id,
                            ref,
                            user_type_id,
                            journal_id,
                            currency_id,
                            date_maturity,
                            blocked,
                            analytic_account_id,
                            payment_mode_id,
                            l10n_nl_date_invoice,
                            start_date,
                            end_date,
                            operating_unit_id,
                            product_id,
                            tax_line_id,
                            product_uom_id,
                            create_uid,                            
                            credit,
                            account_id,
                            invoice_id,
                            bank_payment_line_id,                            
                            tax_exigible,
                            debit_cash_basis,
                            credit_cash_basis,
                            balance_cash_basis,
                            write_date,
                            date,
                            write_uid,
                            move_id,
                            name,
                            debit,
                            amount_currency,
                            quantity,
                            company_currency_id,
                            balance,
                            company_id
                            )
                    SELECT
                            create_date,
                            partner_bank_id,
                            partner_id,
                            ref,
                            user_type_id,
                            journal_id,
                            currency_id,
                            date_maturity,
                            blocked,
                            analytic_account_id,
                            payment_mode_id,
                            l10n_nl_date_invoice,
                            start_date,
                            end_date,                            
                            operating_unit_id,
                            product_id,
                            tax_line_id,
                            product_uom_id,
                            create_uid,                        
                            debit,
                            account_id,
                            invoice_id,
                            bank_payment_line_id,
                            tax_exigible,
                            credit_cash_basis,
                            debit_cash_basis,
                            balance_cash_basis,
                            write_date,
                            date,
                            write_uid,
                            {0} AS move_id,
                            name,
                            credit,
                            amount_currency,
                            quantity,
                            company_currency_id,
                            balance,
                            company_id
                    FROM account_move_line
                    WHERE move_id={1} AND NOT (debit=0 AND credit=0);
        """.format(
                   move_id,
                   self.id
                   ))
        cr.execute(sql_query)
        # move = self.browse(move_id)
        return [move_id]
    
    
    def create_reversals_via_job_sql(self, date=False, journal=False):
        # def create_reversals_via_job_sql(self, date=False, journal
        #                      line_prefix=False, reconcile=False):
        moves = self.env['account.move']
        move_ids = []
        for orig in self:
            if self.env.user.company_id.reversal_via_sql:
                # Create account move and lines using query
                reversal_move_id = orig.create_reversal_moveline_with_query(date, journal)
                move_ids += reversal_move_id
                orig.write({
                    'reverse_entry_id': reversal_move_id[0],
                })
            elif self.env.user.company_id.perform_reversal_by_line_jq :
                # Create account move and lines using job queue
                jq = orig.with_delay(description='Perform reversal via SQL Job queue').create_reversal_move_job_queue(date, journal)
                job_id = self.env['queue.job'].search([('uuid', '=', jq.uuid)])
                orig.job_queue = job_id.id
            elif self.env.user.company_id.reversal_via_jq:
                orig.with_delay(description='Perform reversal via Job queue').create_reversal_via_job_queue(date, journal)
        if move_ids:
            moves = moves.browse(move_ids)
            moves.reconcile()
            moves._post_validate()
            moves.post()
            # if reconcile:
            #     self.move_reverse_reconcile()
        return moves


    # reversal via job queue
    @job
    def create_reversal_via_job_queue(self, date, journal):
        try:
            return self.reverse_moves(date, journal)
        except Exception as e:
            raise Exception(_("The details of the error:'%s'") % (exception_to_unicode(e)))

    # Create account move and lines using job queue
    @job
    def create_reversal_move_job_queue(self, date, journal):
        moves = self.env['account.move']
        try:
            for orig in self:
                reversal_move_id = orig.create_reversal_moveline_with_query(date, journal)
                reversal_move = moves.browse(reversal_move_id)
                moves |= reversal_move
                orig.write({
                    'reverse_entry_id': reversal_move.id,
                })
            if moves:
                moves.reconcile()
                moves._post_validate()
                moves.post()
            return moves

        except Exception:
            raise FailedJobError(
                _("The details of the error:'%s'") % (unicode(e)))
