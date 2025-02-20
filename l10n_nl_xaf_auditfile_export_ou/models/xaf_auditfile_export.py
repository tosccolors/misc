# Copyright 2015-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models, modules, release
from odoo.exceptions import UserError

STATEMENT_UNDIVIDED_PROFIT_BALANCE_OU = """
SELECT SUM(l.balance)
 FROM account_move_line l
 JOIN account_account a
   ON l.account_id = a.id
 JOIN account_account_type t
   ON a.user_type_id = t.id
 WHERE l.parent_state = 'posted'
   AND (l.display_type IS NULL OR
        l.display_type NOT IN ('line_section', 'line_note'))
   AND l.date < %(date_start)s
   AND l.company_id = %(company_id)s
   AND l.operating_unit_id = %(operating_unit_id)s
   AND (
       t.include_initial_balance = false
       OR t.id = %(current_year_earnings_type)s
   )
"""


def chunks(items, n=None):
    """Yield successive n-sized chunks from items."""
    if n is None:
        n = models.PREFETCH_MAX
    for i in range(0, len(items), n):
        yield items[i : i + n]


class XafAuditfileExport(models.Model):
    _inherit = ["xaf.auditfile.export"]
    _description = "XAF auditfile export"

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit', readonly=True,
        default=lambda self: self.env['res.users'].operating_unit_default_get(),
    )

    def get_partners(self):
        """return a generator over partners"""

        if self.operating_unit_id:
            partner_ids = self.get_OU_partners()

        else:
            partner_ids = (
                self.env["res.partner"]
                .search(
                    [
                        "|",
                        ("customer_rank", ">", 0),
                        ("supplier_rank", ">", 0),
                        "|",
                        ("company_id", "=", False),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
                .ids
            )

        self.env.cache.invalidate()
        for chunk in chunks(partner_ids):
            for partner in self.env["res.partner"].browse(chunk):
                yield partner
            self.env.cache.invalidate()

    def get_ob_totals(self):
        """return totals of opening balance"""
        # first get regular opening balances
        # (excluding accounts of type current year earnings)
        cye_type_id = self.env.ref("account.data_unaffected_earnings").id

        ouStr = ''
        if self.operating_unit_id.id:
            ouStr = "and operating_unit_id = %s " % (self.operating_unit_id.id)

        self.env.cr.execute(
            "select sum(l.credit), sum(l.debit), count(distinct a.id) "
            "from account_move_line l, account_account a, "
            "     account_account_type t "
            "where a.user_type_id = t.id "
            "and l.account_id = a.id "
            "and l.parent_state = 'posted' "
            "and (l.display_type IS NULL OR"
            "     l.display_type NOT IN ('line_section', 'line_note')) "
            "and l.date < %s "
            "and l.company_id = %s "
            " " + ouStr + " "
            "and t.include_initial_balance = true "
            "and t.id != %s",
            (self.date_start, self.company_id.id, cye_type_id),
        )
        row = self.env.cr.fetchone()
        credit, debit, account_count = (
            (row[0] or 0.0, row[1] or 0.0, row[2] or 0) if row else (0.0, 0.0, 0)
        )
        # correct for hitherto undistributed profits
        undistributed_profits = self._get_undistributed_profits()
        creditcor, debitcor = (
            (-undistributed_profits, 0.0)
            if undistributed_profits < 0.0
            else (0.0, undistributed_profits)
        )
        countcor = 1 if undistributed_profits else 0
        return dict(
            credit=round(credit + creditcor, 2),
            debit=round(debit + debitcor, 2),
            count=account_count + countcor,
        )

    def get_ob_lines(self):
        """return opening balance entries"""
        cye_type_id = self.env.ref("account.data_unaffected_earnings").id

        ouStr = ''
        if self.operating_unit_id.id:
            ouStr = "and operating_unit_id = %s " % (self.operating_unit_id.id)

        self.env.cr.execute(
            "select a.id, a.code, sum(l.balance) "
            "from account_move_line l, account_account a, "
            "     account_account_type t "
            "where a.user_type_id = t.id "
            "and a.id = l.account_id and l.date < %s "
            "and l.company_id = %s "
            " " + ouStr + " "
            "and l.parent_state = 'posted' "
            "and (l.display_type IS NULL OR"
            "      l.display_type NOT IN ('line_section', 'line_note')) "
            "and t.include_initial_balance = true "
            "and t.id != %s "
            "group by a.id, a.code",
            (self.date_start, self.company_id.id, cye_type_id),
        )
        results = self.env.cr.fetchall()
        # Add line for undistributed profits if any.
        undistributed_profits = self._get_undistributed_profits()
        if undistributed_profits:
            # Now need to find the right account to book them
            row = self._get_undistributed_profit_account()
            if row and row[0]:
                account_id = row[0]
                account_code = row[1]
                results.append([account_id, account_code, undistributed_profits])
        for result in results:
            yield dict(
                account_id=result[0],
                account_code=result[1],
                balance=round(result[2], 2),
            )

    def _get_undistributed_profits(self):
        """Get amount of undistributed profits."""
        if not self.operating_unit_id:
            return super()._get_undistributed_profits()

        current_year_earnings_type = self.env.ref("account.data_unaffected_earnings")
        self.env.cr.execute(
            STATEMENT_UNDIVIDED_PROFIT_BALANCE_OU,
            dict(
                company_id=self.company_id.id,
                operating_unit_id=self.operating_unit_id.id,
                date_start=self.date_start,
                current_year_earnings_type=current_year_earnings_type.id,
            ),
        )
        row = self.env.cr.fetchone()
        if not row or not row[0]:
            return 0.0
        return round(row[0], 2)

    def get_OU_partners(self):
        """return partner of move """
        domain = [
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("state", "=", "posted"),
            ("company_id", "=", self.company_id.id),
        ]

        if self.operating_unit_id:
            domain += [("operating_unit_id", "in", (False, self.operating_unit_id.id))]

        return self.env["account.move"].search(domain).mapped('partner_id').ids


    def get_move_line_count(self):
        """return amount of move lines"""
        domain = [
            ("date", ">=", self.date_start),
            ("date", "<=", self.date_end),
            ("parent_state", "=", "posted"),
            ("display_type", "not in", ("line_section", "line_note")),
            ("company_id", "=", self.company_id.id),
        ]

        if self.operating_unit_id:
            domain += [("operating_unit_id", "=", self.operating_unit_id.id)]

        return self.env["account.move.line"].search_count(domain)

    def get_move_line_total_debit(self):
        """return total debit of move lines"""
        ouStr = ''
        if self.operating_unit_id.id:
            ouStr = "and operating_unit_id = %s "%(self.operating_unit_id.id)

        self.env.cr.execute(
            "select sum(debit) from account_move_line "
            "where date >= %s "
            "and date <= %s "
            "and parent_state = 'posted' "
            "and (display_type IS NULL OR"
            "     display_type NOT IN ('line_section', 'line_note')) "
            "and company_id = %s "
            " " + ouStr + " ",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return round(self.env.cr.fetchall()[0][0] or 0.0, 2)

    def get_move_line_total_credit(self):
        """return total credit of move lines"""
        ouStr = ''
        if self.operating_unit_id.id:
            ouStr = "and operating_unit_id = %s "%(self.operating_unit_id.id)

        self.env.cr.execute(
            "select sum(credit) from account_move_line "
            "where date >= %s "
            "and date <= %s "
            "and parent_state = 'posted' "
            "and (display_type IS NULL OR"
            "     display_type NOT IN ('line_section', 'line_note')) "
            "and company_id = %s "
            " " + ouStr + " ",
            (self.date_start, self.date_end, self.company_id.id),
        )
        return round(self.env.cr.fetchall()[0][0] or 0.0, 2)

    def get_journals(self):
        """return journals"""
        domain = [("company_id", "=", self.company_id.id)]
        if self.operating_unit_id:
            domain += [('operating_unit_id', 'in', (False, self.operating_unit_id.id))]

        return (
            self.env["account.journal"]
            .with_context(active_test=False)
            .search(domain)
        )

    def get_moves(self, journal):
        """return moves for a journal, generator style"""
        domain = [
                    ("date", ">=", self.date_start),
                    ("date", "<=", self.date_end),
                    ("journal_id", "=", journal.id),
                    ("state", "=", "posted"),
                ]

        if self.operating_unit_id:
            domain += [("operating_unit_id", "=", self.operating_unit_id.id)]

        move_ids = (
            self.env["account.move"]
            .search(domain)
            .ids
        )
        self.env.cache.invalidate()
        for chunk in chunks(move_ids):
            for move in self.env["account.move"].browse(chunk):
                yield move
            self.env.cache.invalidate()
