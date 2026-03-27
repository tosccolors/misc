# Copyright 2015-2023 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from odoo import _, api, exceptions, fields, models, modules, release
from odoo.exceptions import UserError


class XafAuditfileExport(models.Model):
    _inherit = "xaf.auditfile.export"

    operating_unit_id = fields.Many2one(
        'operating.unit', 'Operating Unit',
        default=lambda self: self.env['res.users'].operating_unit_default_get(),
    )

    def get_ob_totals(self):
        with self._adjust_statement_for_ou(
            "select sum(l.credit), sum(l.debit), count(distinct a.id) ",
            "and l.company_id = %s",
            f"and l.operating_unit_id = {self.operating_unit_id.id} and l.company_id = %s",
        ):
            return super().get_ob_totals()

    def get_ob_lines(self):
        with self._adjust_statement_for_ou(
                "select a.id, a.code, sum(l.balance) ",
                "and l.company_id = %s", 
                f"and l.operating_unit_id = {self.operating_unit_id.id} and l.company_id = %s",
        ):
            yield from super().get_ob_lines()

    def _get_undistributed_profits(self):
        with self._adjust_statement_for_ou(
                "\nSELECT SUM(l.balance)",
                "   AND l.company_id = %(company_id)s",
                f"   AND l.operating_unit_id = {self.operating_unit_id.id} AND l.company_id = %(company_id)s",
        ):
            return super()._get_undistributed_profits()

    def _get_undistributed_profit_account(self):
        with self._adjust_statement_for_ou(
                "\nWITH find_undivided_profit_code AS (",
                " WHERE company_id = %(company_id)s",
                f" WHERE operating_unit_id = {self.operating_unit_id.id} AND company_id = %(company_id)s",
        ), self._adjust_statement_for_ou(
                "\nWITH find_undivided_profit_code AS (",
                " WHERE a.company_id = %(company_id)s",
                f" WHERE a.operating_unit_id = {self.operating_unit_id.id} AND a.company_id = %(company_id)s",
        ):
            return super()._get_undistributed_profit_account()

    def get_move_line_count(self):
        self = self.with_context(l10n_nl_xaf_auditfile_export_ou=self.operating_unit_id)
        return super().get_move_line_count()

    def get_move_line_total_debit(self):
        with self._adjust_statement_for_ou(
                "select sum(debit) from account_move_line ",
                "and company_id = %s",
                f"and operating_unit_id = {self.operating_unit_id.id} and company_id = %s",
        ):
            return super().get_move_line_total_debit()

    def get_move_line_total_credit(self):
        with self._adjust_statement_for_ou(
                "select sum(credit) from account_move_line ",
                "and company_id = %s",
                f"and operating_unit_id = {self.operating_unit_id.id} and company_id = %s",
        ):
            return super().get_move_line_total_credit()

    def get_journals(self):
        self = self.with_context(l10n_nl_xaf_auditfile_export_ou=self.operating_unit_id)
        return super().get_journals()

    def get_moves(self, journal):
        self = self.with_context(l10n_nl_xaf_auditfile_export_ou=self.operating_unit_id)
        return super().get_moves(journal)
 
    @contextmanager
    def _adjust_statement_for_ou(self, statement_start, needle, replacement):
        original_execute = self.env.cr.execute

        def preprocess_execute(statement, *args, **kwargs):
            if statement.startswith(statement_start):
                statement = statement.replace(needle, replacement)

            return original_execute(statement, *args, **kwargs)

        if self.operating_unit_id:
            self.env.cr.execute = preprocess_execute

        try:
            yield
        finally:   
            self.env.cr.execute = original_execute


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def _search(self, args, *pargs, **kwargs):
        ou = self.env.context.get('l10n_nl_xaf_auditfile_export_ou')
        if ou:
            args += [('operating_unit_id', '=', ou.id)]
        return super()._search(args, *pargs, **kwargs)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _search(self, args, *pargs, **kwargs):
        ou = self.env.context.get('l10n_nl_xaf_auditfile_export_ou')
        if ou:
            args += ['|', ('move_id.operating_unit_id', '=', ou.id), ('operating_unit_id', '=', ou.id)]
        return super()._search(args, *pargs, **kwargs)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def _search(self, args, *pargs, **kwargs):
        ou = self.env.context.get('l10n_nl_xaf_auditfile_export_ou')
        if ou:
            args += ['|', ('operating_unit_id', '=', False), ('operating_unit_id', '=', ou.id)]
        return super()._search(args, *pargs, **kwargs)
