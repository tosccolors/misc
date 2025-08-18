# Copyright 2025 Hunki Enterprises BV
from odoo import models


class AccountStatementImport(models.TransientModel):
    _inherit = "account.statement.import"

    def _match_journal(self, account_number, currency):
        """Force journal from context to avoid problems with EUR/USD journal"""
        journal = (
            self.env["account.journal"]
            .browse(self.env.context.get("journal_id") or [])
            .exists()
        )
        if journal and journal.currency_id == currency:
            return journal
        return super()._match_journal(account_number, currency)
