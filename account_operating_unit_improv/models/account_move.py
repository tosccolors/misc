from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("journal_id")
    def _onchange_journal(self):
        """Reset move's OU if journal doesn't have an OU"""
        result = super()._onchange_journal()
        self.operating_unit_id = self.journal_id.operating_unit_id
        return result

    @api.onchange("operating_unit_id")
    def _onchange_operating_unit(self):
        """
        Keep lines' OUs regardless of changed move OU.
        Also keep journal if it didn't have an OU, as super will overwrite it with one
        that does, which is undesired behavior.
        """
        line2ou = {line: line.operating_unit_id for line in self.line_ids}
        journal = self.journal_id
        result = super()._onchange_operating_unit()
        for line in self.line_ids:
            line.operating_unit_id = line2ou[line]
        if journal and not journal.operating_unit_id:
            self.journal_id = journal
        return result

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids(self):
        """Undo super's assigning move's OU on lines"""
        line2ou = {line: line.operating_unit_id for line in self.invoice_line_ids}
        result = super()._onchange_invoice_line_ids()
        for line in self.invoice_line_ids:
            line.operating_unit_id = line2ou[line]
        return result

    def _prepare_inter_ou_balancing_move_line(self, move, ou_id, ou_balances):
        """Add exclude_from_invoice_tab for balancing lines"""
        result = super()._prepare_inter_ou_balancing_move_line(move, ou_id, ou_balances)
        result['exclude_from_invoice_tab'] = True
        return result
