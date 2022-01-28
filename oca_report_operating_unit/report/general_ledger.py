# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class GeneralLedgerReport(models.TransientModel):
    _inherit = 'report_general_ledger'

    operating_unit_id = fields.Many2one(comodel_name='operating.unit')

class GeneralLedgerReportCompute(models.TransientModel):
    """ Here, we just define methods.
    For class fields, go more top at this file.
    """

    _inherit = 'report_general_ledger'

    def _get_account_sub_subquery_sum_amounts(
            self, include_initial_balance, date_included):
        """ Return subquery used to compute sum amounts on accounts """
        sub_subquery_sum_amounts = """
            SELECT
                a.id AS account_id,
                SUM(ml.debit) AS debit,
                SUM(ml.credit) AS credit,
                SUM(ml.balance) AS balance,
                c.id AS currency_id,
                CASE
                    WHEN c.id IS NOT NULL
                    THEN SUM(ml.amount_currency)
                    ELSE NULL
                END AS balance_currency
            FROM
                accounts a
            INNER JOIN
                account_account_type at ON a.user_type_id = at.id
            INNER JOIN
                account_move_line ml
                    ON a.id = ml.account_id
        """
        #@sushma
        if self.operating_unit_id:
            sub_subquery_sum_amounts += """
                AND ml.operating_unit_id = %s
            """%self.operating_unit_id.id

        if date_included:
            sub_subquery_sum_amounts += """
                AND ml.date <= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND ml.date < %s
            """

        if not include_initial_balance:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance != TRUE AND ml.date >= %s
            """
        else:
            sub_subquery_sum_amounts += """
                AND at.include_initial_balance = TRUE
            """

        if self.only_posted_moves:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_move m ON ml.move_id = m.id AND m.state = 'posted'
            """
        if self.filter_cost_center_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_analytic_account aa
                ON
                    ml.analytic_account_id = aa.id
                    AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        sub_subquery_sum_amounts += """
        LEFT JOIN
            res_currency c ON a.currency_id = c.id
        """
        sub_subquery_sum_amounts += """
        GROUP BY
            a.id, c.id
        """
        return sub_subquery_sum_amounts

    def _get_partner_sub_subquery_sum_amounts(
            self, only_empty_partner, include_initial_balance, date_included
    ):
        """ Return subquery used to compute sum amounts on partners """
        sub_subquery_sum_amounts = """
            SELECT
                ap.account_id AS account_id,
                ap.partner_id AS partner_id,
                SUM(ml.debit) AS debit,
                SUM(ml.credit) AS credit,
                SUM(ml.balance) AS balance,
                c.id as currency_id,
                CASE
                    WHEN c.id IS NOT NULL
                    THEN SUM(ml.amount_currency)
                    ELSE NULL
                END AS balance_currency
            FROM
                accounts_partners ap
            INNER JOIN account_account ac
            ON ac.id = ap.account_id
            LEFT JOIN
                res_currency c ON ac.currency_id = c.id
            INNER JOIN
                account_move_line ml
                    ON ap.account_id = ml.account_id
            """
        # @sushma
        if self.operating_unit_id:
            sub_subquery_sum_amounts += """
                        AND ml.operating_unit_id = %s
                    """ % self.operating_unit_id.id
        if date_included:
            sub_subquery_sum_amounts += """
                    AND ml.date <= %s
            """
        else:
            sub_subquery_sum_amounts += """
                    AND ml.date < %s
            """
        if not only_empty_partner:
            sub_subquery_sum_amounts += """
                    AND ap.partner_id = ml.partner_id
            """
        else:
            sub_subquery_sum_amounts += """
                    AND ap.partner_id IS NULL AND ml.partner_id IS NULL
            """
        if not include_initial_balance:
            sub_subquery_sum_amounts += """
                    AND ap.include_initial_balance != TRUE AND ml.date >= %s
            """
        else:
            sub_subquery_sum_amounts += """
                    AND ap.include_initial_balance = TRUE
            """
        if self.only_posted_moves:
            sub_subquery_sum_amounts += """
            INNER JOIN
                account_move m ON ml.move_id = m.id AND m.state = 'posted'
            """
        if self.filter_cost_center_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            account_analytic_account aa
                ON
                    ml.analytic_account_id = aa.id
                    AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            sub_subquery_sum_amounts += """
        INNER JOIN
            move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        sub_subquery_sum_amounts += """
            GROUP BY
                ap.account_id, ap.partner_id, c.id
        """
        return sub_subquery_sum_amounts

    def _inject_partner_values(self, only_empty_partner=False):
        """ Inject report values for report_general_ledger_qweb_partner.

        Only for "partner" accounts (payable and receivable).
        """
        # pylint: disable=sql-injection
        query_inject_partner = """
        WITH
            accounts_partners AS
                (
                    SELECT
                        ra.id AS report_account_id,
                        a.id AS account_id,
                        at.include_initial_balance AS include_initial_balance,
                        p.id AS partner_id,
                        COALESCE(
                            CASE
                                WHEN
                                    NULLIF(p.name, '') IS NOT NULL
                                    AND NULLIF(p.ref, '') IS NOT NULL
                                THEN p.name || ' (' || p.ref || ')'
                                ELSE p.name
                            END,
                            '""" + _('No partner allocated') + """'
                        ) AS partner_name
                    FROM
                        report_general_ledger_qweb_account ra
                    INNER JOIN
                        account_account a ON ra.account_id = a.id
                    INNER JOIN
                        account_account_type at ON a.user_type_id = at.id
                    INNER JOIN
                        account_move_line ml ON a.id = ml.account_id
                    LEFT JOIN
                        res_partner p ON ml.partner_id = p.id
                    """
        if self.filter_cost_center_ids:
            query_inject_partner += """
            INNER JOIN
                account_analytic_account aa
                    ON
                        ml.analytic_account_id = aa.id
                        AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            query_inject_partner += """
            INNER JOIN
                account_analytic_tag_account_move_line_rel atml
                    ON atml.account_move_line_id = ml.id
            INNER JOIN
                account_analytic_tag aat
                    ON
                        atml.account_analytic_tag_id = aat.id
                        AND aat.id IN %s
            """
        query_inject_partner += """
            WHERE
                ra.report_id = %s
            AND
                ra.is_partner_account = TRUE
        """
        if not only_empty_partner:
            query_inject_partner += """
            AND
                p.id IS NOT NULL
            """
        else:
            query_inject_partner += """
            AND
                p.id IS NULL
            """
        query_inject_partner += """
                        """
        if self.centralize:
            query_inject_partner += """
            AND (a.centralized IS NULL OR a.centralized != TRUE)
            """
        if self.filter_partner_ids:
            query_inject_partner += """
            AND
                p.id IN %s
            """
        # @sushma
        if self.operating_unit_id:
            query_inject_partner += """
            AND
                ml.operating_unit_id = %s
            """
        init_subquery = self._get_final_partner_sub_subquery_sum_amounts(
            only_empty_partner,
            date_included=False
        )
        final_subquery = self._get_final_partner_sub_subquery_sum_amounts(
            only_empty_partner,
            date_included=True
        )

        query_inject_partner += """
            GROUP BY
                ra.id,
                a.id,
                p.id,
                at.include_initial_balance
        ),
        """

        if self.filter_analytic_tag_ids:
            query_inject_partner += """
    move_lines_on_tags AS
        (
            SELECT
                DISTINCT ml.id AS ml_id
            FROM
                accounts_partners ap
            INNER JOIN
                account_move_line ml
                    ON ap.account_id = ml.account_id
            INNER JOIN
                account_analytic_tag_account_move_line_rel atml
                    ON atml.account_move_line_id = ml.id
            INNER JOIN
                account_analytic_tag aat
                    ON
                        atml.account_analytic_tag_id = aat.id
            WHERE
                aat.id IN %s
        ),
            """

        query_inject_partner += """
    initial_sum_amounts AS ( """ + init_subquery + """ ),
    final_sum_amounts AS ( """ + final_subquery + """ )
INSERT INTO
    report_general_ledger_qweb_partner
    (
    report_account_id,
    create_uid,
    create_date,
    partner_id,
    name,
    initial_debit,
    initial_credit,
    initial_balance,
    currency_id,
    initial_balance_foreign_currency,
    final_debit,
    final_credit,
    final_balance,
    final_balance_foreign_currency
    )
SELECT
    ap.report_account_id,
    %s AS create_uid,
    NOW() AS create_date,
    ap.partner_id,
    ap.partner_name,
    COALESCE(i.debit, 0.0) AS initial_debit,
    COALESCE(i.credit, 0.0) AS initial_credit,
    COALESCE(i.balance, 0.0) AS initial_balance,
    i.currency_id AS currency_id,
    COALESCE(i.balance_currency, 0.0) AS initial_balance_foreign_currency,
    COALESCE(f.debit, 0.0) AS final_debit,
    COALESCE(f.credit, 0.0) AS final_credit,
    COALESCE(f.balance, 0.0) AS final_balance,
    COALESCE(f.balance_currency, 0.0) AS final_balance_foreign_currency
FROM
    accounts_partners ap
LEFT JOIN
    initial_sum_amounts i
        ON
            (
        """
        if not only_empty_partner:
            query_inject_partner += """
                ap.partner_id = i.partner_id
            """
        else:
            query_inject_partner += """
                ap.partner_id IS NULL AND i.partner_id IS NULL
            """
        query_inject_partner += """
            )
            AND ap.account_id = i.account_id
LEFT JOIN
    final_sum_amounts f
        ON
            (
        """
        if not only_empty_partner:
            query_inject_partner += """
                ap.partner_id = f.partner_id
            """
        else:
            query_inject_partner += """
                ap.partner_id IS NULL AND f.partner_id IS NULL
            """
        query_inject_partner += """
            )
            AND ap.account_id = f.account_id
WHERE
    (
        i.debit IS NOT NULL AND i.debit != 0
        OR i.credit IS NOT NULL AND i.credit != 0
        OR i.balance IS NOT NULL AND i.balance != 0
        OR f.debit IS NOT NULL AND f.debit != 0
        OR f.credit IS NOT NULL AND f.credit != 0
        OR f.balance IS NOT NULL AND f.balance != 0
    )
        """
        if self.hide_account_at_0:
            query_inject_partner += """
AND
    f.balance IS NOT NULL AND f.balance != 0
            """
        query_inject_partner_params = ()
        if self.filter_cost_center_ids:
            query_inject_partner_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        if self.filter_analytic_tag_ids:
            query_inject_partner_params += (
                tuple(self.filter_analytic_tag_ids.ids),
            )
        query_inject_partner_params += (
            self.id,
        )
        if self.filter_partner_ids:
            query_inject_partner_params += (
                tuple(self.filter_partner_ids.ids),
            )
        #@sushma
        if self.operating_unit_id:
            query_inject_partner_params += (
                self.operating_unit_id.id,
            )
        if self.filter_analytic_tag_ids:
            query_inject_partner_params += (
                tuple(self.filter_analytic_tag_ids.ids),
            )
        query_inject_partner_params += (
            self.date_from,
            self.fy_start_date,
        )
        if self.filter_cost_center_ids:
            query_inject_partner_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_partner_params += (
            self.date_from,
        )
        if self.filter_cost_center_ids:
            query_inject_partner_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_partner_params += (
            self.date_to,
            self.fy_start_date,
        )
        if self.filter_cost_center_ids:
            query_inject_partner_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_partner_params += (
            self.date_to,
        )
        if self.filter_cost_center_ids:
            query_inject_partner_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_partner_params += (
            self.env.uid,
        )
        self.env.cr.execute(query_inject_partner, query_inject_partner_params)

    def _inject_line_not_centralized_values(
            self,
            is_account_line=True,
            is_partner_line=False,
            only_empty_partner_line=False,
            only_unaffected_earnings_account=False):
        """ Inject report values for report_general_ledger_qweb_move_line.

        If centralized option have been chosen,
        only non centralized accounts are computed.

        In function of `is_account_line` and `is_partner_line` values,
        the move_line link is made either with account or either with partner.

        The "only_empty_partner_line" value is used
        to compute data without partner.
        """

        query_inject_move_line = ""
        if self.filter_analytic_tag_ids:
            query_inject_move_line += """
WITH
    move_lines_on_tags AS
        (
            SELECT
                DISTINCT ml.id AS ml_id
            FROM
        """
            if is_account_line:
                query_inject_move_line += """
                report_general_ledger_qweb_account ra
            """
            elif is_partner_line:
                query_inject_move_line += """
                report_general_ledger_qweb_partner rp
            INNER JOIN
                report_general_ledger_qweb_account ra
                    ON rp.report_account_id = ra.id
            """
            query_inject_move_line += """
            INNER JOIN
                account_move_line ml
                    ON ra.account_id = ml.account_id
            INNER JOIN
                account_analytic_tag_account_move_line_rel atml
                    ON atml.account_move_line_id = ml.id
            INNER JOIN
                account_analytic_tag aat
                    ON
                        atml.account_analytic_tag_id = aat.id
            WHERE
                ra.report_id = %s
            AND
                aat.id IN %s
        )
            """
        query_inject_move_line += """
INSERT INTO
    report_general_ledger_qweb_move_line
    (
        """
        if is_account_line:
            query_inject_move_line += """
    report_account_id,
            """
        elif is_partner_line:
            query_inject_move_line += """
    report_partner_id,
            """
        query_inject_move_line += """
    create_uid,
    create_date,
    move_line_id,
    matched_ml_id,
    date,
    entry,
    journal,
    account,
    taxes_description,
    partner,
    label,
    cost_center,
    debit,
    credit,
    cumul_balance,
    currency_id,
    amount_currency
    )
SELECT
        """
        if is_account_line:
            query_inject_move_line += """
    ra.id AS report_account_id,
            """
        elif is_partner_line:
            query_inject_move_line += """
    rp.id AS report_partner_id,
            """
        query_inject_move_line += """
    %s AS create_uid,
    NOW() AS create_date,
    ml.id AS move_line_id,
    fr.id AS matched_ml_id,
    ml.date,
    m.name AS entry,
    j.code AS journal,
    a.code AS account,
    CASE
        WHEN
            ml.tax_line_id is not null
        THEN
            COALESCE(at.description, at.name)
        WHEN
            ml.tax_line_id is null
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
                aml_at_rel.account_move_line_id = ml.id)
        ELSE
            ''
    END as taxes_description,
        """
        if not only_empty_partner_line:
            query_inject_move_line += """
    CASE
        WHEN
            NULLIF(p.name, '') IS NOT NULL
            AND NULLIF(p.ref, '') IS NOT NULL
        THEN p.name || ' (' || p.ref || ')'
        ELSE p.name
    END AS partner,
            """
        elif only_empty_partner_line:
            query_inject_move_line += """
    '""" + _('No partner allocated') + """' AS partner,
            """
        query_inject_move_line += """
    CONCAT_WS(' - ', NULLIF(ml.ref, ''), NULLIF(ml.name, '')) AS label,
    aa.name AS cost_center,
    ml.debit,
    ml.credit,
        """
        if is_account_line:
            query_inject_move_line += """
    ra.initial_balance + (
        SUM(ml.balance)
        OVER (PARTITION BY a.code
              ORDER BY a.code, ml.date, ml.id)
    ) AS cumul_balance,
            """
        elif is_partner_line and not only_empty_partner_line:
            query_inject_move_line += """
    rp.initial_balance + (
        SUM(ml.balance)
        OVER (PARTITION BY a.code, p.name
              ORDER BY a.code, p.name, ml.date, ml.id)
    ) AS cumul_balance,
            """
        elif is_partner_line and only_empty_partner_line:
            query_inject_move_line += """
    rp.initial_balance + (
        SUM(ml.balance)
        OVER (PARTITION BY a.code
              ORDER BY a.code, ml.date, ml.id)
    ) AS cumul_balance,
            """
        query_inject_move_line += """
    c.id AS currency_id,
    ml.amount_currency
FROM
        """
        if is_account_line:
            query_inject_move_line += """
    report_general_ledger_qweb_account ra
            """
        elif is_partner_line:
            query_inject_move_line += """
    report_general_ledger_qweb_partner rp
INNER JOIN
    report_general_ledger_qweb_account ra ON rp.report_account_id = ra.id
            """
        query_inject_move_line += """
INNER JOIN
    account_move_line ml ON ra.account_id = ml.account_id
INNER JOIN
    account_move m ON ml.move_id = m.id
INNER JOIN
    account_journal j ON ml.journal_id = j.id
INNER JOIN
    account_account a ON ml.account_id = a.id
LEFT JOIN
    account_tax at ON ml.tax_line_id = at.id
        """
        if is_account_line:
            query_inject_move_line += """
LEFT JOIN
    res_partner p ON ml.partner_id = p.id
            """
        elif is_partner_line and not only_empty_partner_line:
            query_inject_move_line += """
INNER JOIN
    res_partner p
        ON ml.partner_id = p.id AND rp.partner_id = p.id
            """
        query_inject_move_line += """
LEFT JOIN
    account_full_reconcile fr ON ml.full_reconcile_id = fr.id
LEFT JOIN
    res_currency c ON ml.currency_id = c.id
                    """
        if self.filter_cost_center_ids:
            query_inject_move_line += """
INNER JOIN
    account_analytic_account aa
        ON
            ml.analytic_account_id = aa.id
            AND aa.id IN %s
            """
        else:
            query_inject_move_line += """
LEFT JOIN
    account_analytic_account aa ON ml.analytic_account_id = aa.id
            """
        if self.filter_analytic_tag_ids:
            query_inject_move_line += """
INNER JOIN
    move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        query_inject_move_line += """
WHERE
    ra.report_id = %s
AND
        """
        if only_unaffected_earnings_account:
            query_inject_move_line += """
    a.id = %s
AND
            """
        if is_account_line:
            query_inject_move_line += """
    (ra.is_partner_account IS NULL OR ra.is_partner_account != TRUE)
            """
        elif is_partner_line:
            query_inject_move_line += """
    ra.is_partner_account = TRUE
            """
        if self.centralize:
            query_inject_move_line += """
AND
    (a.centralized IS NULL OR a.centralized != TRUE)
            """
        query_inject_move_line += """
AND
    ml.date BETWEEN %s AND %s
        """
        if self.only_posted_moves:
            query_inject_move_line += """
AND
    m.state = 'posted'
        """
        if only_empty_partner_line:
            query_inject_move_line += """
AND
    ml.partner_id IS NULL
AND
    rp.partner_id IS NULL
        """
        if self.filter_journal_ids:
            query_inject_move_line += """
AND
    j.id IN %s
            """
        # @sushma
        if self.operating_unit_id:
            query_inject_move_line += """
            AND
                ml.operating_unit_id = %s
                        """
        if is_account_line:
            query_inject_move_line += """
ORDER BY
    a.code, ml.date, ml.id
            """
        elif is_partner_line and not only_empty_partner_line:
            query_inject_move_line += """
ORDER BY
    a.code, p.name, ml.date, ml.id
            """
        elif is_partner_line and only_empty_partner_line:
            query_inject_move_line += """
ORDER BY
    a.code, ml.date, ml.id
            """

        query_inject_move_line_params = ()
        if self.filter_analytic_tag_ids:
            query_inject_move_line_params += (
                self.id,
                tuple(self.filter_analytic_tag_ids.ids),
            )
        query_inject_move_line_params += (
            self.env.uid,
        )
        if self.filter_cost_center_ids:
            query_inject_move_line_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_move_line_params += (
            self.id,
        )
        if only_unaffected_earnings_account:
            query_inject_move_line_params += (
                self.unaffected_earnings_account.id,
            )
        query_inject_move_line_params += (
            self.date_from,
            self.date_to,
        )
        if self.filter_journal_ids:
            query_inject_move_line_params += (tuple(
                self.filter_journal_ids.ids,
            ),)
        # @sushma
        if self.operating_unit_id:
            query_inject_move_line_params += (
                self.operating_unit_id.id,)
        self.env.cr.execute(
            query_inject_move_line,
            query_inject_move_line_params
        )

    def _inject_line_centralized_values(self):
        """ Inject report values for report_general_ledger_qweb_move_line.

        Only centralized accounts are computed.
        """

        if self.filter_analytic_tag_ids:
            query_inject_move_line_centralized = """
WITH
    move_lines_on_tags AS
        (
            SELECT
                DISTINCT ml.id AS ml_id
            FROM
                report_general_ledger_qweb_account ra
            INNER JOIN
                account_move_line ml
                    ON ra.account_id = ml.account_id
            INNER JOIN
                account_analytic_tag_account_move_line_rel atml
                    ON atml.account_move_line_id = ml.id
            INNER JOIN
                account_analytic_tag aat
                    ON
                        atml.account_analytic_tag_id = aat.id
            WHERE
                ra.report_id = %s
            AND
                aat.id IN %s
        ),
            """
        else:
            query_inject_move_line_centralized = """
WITH
            """
        query_inject_move_line_centralized += """
    move_lines AS
        (
            SELECT
                ml.account_id,
                (
                    DATE_TRUNC('month', ml.date) + interval '1 month'
                                                 - interval '1 day'
                )::date AS date,
                SUM(ml.debit) AS debit,
                SUM(ml.credit) AS credit,
                SUM(ml.balance) AS balance,
                ml.currency_id AS currency_id,
                ml.journal_id as journal_id
            FROM
                report_general_ledger_qweb_account ra
            INNER JOIN
                account_move_line ml ON ra.account_id = ml.account_id
            INNER JOIN
                account_move m ON ml.move_id = m.id
            INNER JOIN
                account_account a ON ml.account_id = a.id
        """
        if self.filter_cost_center_ids:
            query_inject_move_line_centralized += """
            INNER JOIN
                account_analytic_account aa
                    ON
                        ml.analytic_account_id = aa.id
                        AND aa.id IN %s
            """
        if self.filter_analytic_tag_ids:
            query_inject_move_line_centralized += """
            INNER JOIN
                move_lines_on_tags ON ml.id = move_lines_on_tags.ml_id
            """
        query_inject_move_line_centralized += """
            WHERE
                ra.report_id = %s
            AND
                a.centralized = TRUE
            AND
                ml.date BETWEEN %s AND %s
        """
        if self.only_posted_moves:
            query_inject_move_line_centralized += """
            AND
                m.state = 'posted'
            """
        # @sushma
        if self.operating_unit_id:
            query_inject_move_line_centralized += """
                               AND
                                   ml.operating_unit_id = %s
                               """%self.operating_unit_id.id
        query_inject_move_line_centralized += """
            GROUP BY
                ra.id, ml.account_id, a.code, 2, ml.currency_id, ml.journal_id
        )
INSERT INTO
    report_general_ledger_qweb_move_line
    (
    report_account_id,
    create_uid,
    create_date,
    date,
    account,
    journal,
    label,
    debit,
    credit,
    cumul_balance
    )
SELECT
    ra.id AS report_account_id,
    %s AS create_uid,
    NOW() AS create_date,
    ml.date,
    a.code AS account,
    j.code as journal,
    '""" + _('Centralized Entries') + """' AS label,
    ml.debit AS debit,
    ml.credit AS credit,
    ra.initial_balance + (
        SUM(ml.balance)
        OVER (PARTITION BY a.code ORDER BY ml.date)
    ) AS cumul_balance
FROM
    report_general_ledger_qweb_account ra
INNER JOIN
    move_lines ml ON ra.account_id = ml.account_id
INNER JOIN
    account_account a ON ml.account_id = a.id
INNER JOIN
    account_journal j ON ml.journal_id = j.id
LEFT JOIN
    res_currency c ON ml.currency_id = c.id
WHERE
    ra.report_id = %s
AND
    (a.centralized IS NOT NULL AND a.centralized = TRUE)
    """
        if self.filter_journal_ids:
            query_inject_move_line_centralized += """
AND
    j.id in %s
            """

        query_inject_move_line_centralized += """
ORDER BY
    a.code, ml.date
        """

        query_inject_move_line_centralized_params = ()
        if self.filter_analytic_tag_ids:
            query_inject_move_line_centralized_params += (
                self.id,
                tuple(self.filter_analytic_tag_ids.ids),
            )
        if self.filter_cost_center_ids:
            query_inject_move_line_centralized_params += (
                tuple(self.filter_cost_center_ids.ids),
            )
        query_inject_move_line_centralized_params += (
            self.id,
            self.date_from,
            self.date_to,
            self.env.uid,
            self.id,
        )
        if self.filter_journal_ids:
            query_inject_move_line_centralized_params += (tuple(
                self.filter_journal_ids.ids,
            ),)
        self.env.cr.execute(
            query_inject_move_line_centralized,
            query_inject_move_line_centralized_params
        )
