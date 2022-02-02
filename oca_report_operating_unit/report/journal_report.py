# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ReportJournalQweb(models.TransientModel):

    _inherit = 'report_journal_ledger'

    operating_unit_id = fields.Many2one(comodel_name='operating.unit')

    @api.multi
    def _inject_move_line_values(self):
        self.ensure_one()
        sql = """
            DELETE
            FROM report_journal_qweb_move_line
            WHERE report_id = %s
        """
        params = (
            self.id,
        )
        self.env.cr.execute(sql, params)
        sql = """
            INSERT INTO report_journal_qweb_move_line (
                create_uid,
                create_date,
                report_id,
                report_journal_id,
                report_move_id,
                move_line_id,
                account_id,
                account,
                account_code,
                account_type,
                partner_id,
                partner,
                date,
                entry,
                label,
                debit,
                credit,
                company_currency_id,
                amount_currency,
                currency_id,
                currency_name,
                tax_id,
                taxes_description,
                company_id
            )
            SELECT
                %s as create_uid,
                NOW() as create_date,
                rjqm.report_id as report_id,
                rjqm.report_journal_id as report_journal_id,
                rjqm.id as report_move_id,
                aml.id as move_line_id,
                aml.account_id as account_id,
                aa.name as account,
                aa.code as account_code,
                aa.internal_type as account_type,
                aml.partner_id as partner_id,
                p.name as partner,
                aml.date as date,
                rjqm.name as entry,
                aml.name as label,
                aml.debit as debit,
                aml.credit as credit,
                aml.company_currency_id as currency_id,
                aml.amount_currency as amount_currency,
                aml.currency_id as currency_id,
                currency.name as currency_name,
                aml.tax_line_id as tax_id,
                CASE
                    WHEN
                      aml.tax_line_id is not null
                THEN
                    COALESCE(at.description, at.name)
                WHEN
                    aml.tax_line_id is null
                THEN
                    (SELECT
                      array_to_string(
                          array_agg(COALESCE(at.description, at.name)
                      ), ', ')
                    FROM
                        account_move_line_account_tax_rel aml_at_rel
                    LEFT JOIN
                        account_tax at on (at.id = aml_at_rel.account_tax_id)
                    WHERE
                        aml_at_rel.account_move_line_id = aml.id)
                ELSE
                    ''
                END as taxes_description,
                aml.company_id as company_id
            FROM
                account_move_line aml
            INNER JOIN
                report_journal_qweb_move rjqm
                    on (rjqm.move_id = aml.move_id)
            LEFT JOIN
                account_account aa
                    on (aa.id = aml.account_id)
            LEFT JOIN
                res_partner p
                    on (p.id = aml.partner_id)
            LEFT JOIN
                account_tax at
                    on (at.id = aml.tax_line_id)
            LEFT JOIN
                res_currency currency
                    on (currency.id = aml.currency_id)
            WHERE
                rjqm.report_id = %s
        """
        # @sushma
        if self.operating_unit_id:
            sql += """
                AND aml.operating_unit_id = %s
            """ % self.operating_unit_id.id
        params = (
            self.env.uid,
            self.id,
        )
        self.env.cr.execute(sql, params)