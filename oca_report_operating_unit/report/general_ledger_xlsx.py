# -*- coding: utf-8 -*-
from odoo.addons.account_financial_report_qweb.report import abstract_report_xlsx
from odoo.report import report_sxw
from odoo import _


class GeneralLedgerXslx(abstract_report_xlsx.AbstractReportXslx):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(GeneralLedgerXslx, self).__init__(
            name, table, rml, parser, header, store)

    def _get_report_name(self):
        return _('General Ledger123123')


    def _get_report_filters(self, report):
        return [
            [
                _('Date range filter'),
                _('From: %s To: %s') % (report.date_from, report.date_to),
            ],
            [
                _('Target moves filter'),
                _('All posted entries') if report.only_posted_moves
                else _('All entries'),
            ],
            [
                _('Account balance at 0 filter'),
                _('Hide') if report.hide_account_balance_at_0 else _('Show'),
            ],
            [
                _('Centralize filter'),
                _('Yes') if report.centralize else _('No'),
            ],
            [
                _('Show analytic tags'),
                _('Yes') if report.show_analytic_tags else _('No'),
            ],
            [
                _('Show foreign currency'),
                _('Yes') if report.foreign_currency else _('No')
            ],
            [
                _('Operating Unit'),
                _(report.operating_unit_id.name) if report.operating_unit_id else _('No')
            ],
        ]


GeneralLedgerXslx(
    'report.oca_report_operating_unit.report_general_ledger_xlsx',
    # 'report.account_financial_report_qweb.report_general_ledger_xlsx',
    'report_general_ledger',
    parser=report_sxw.rml_parse
)
