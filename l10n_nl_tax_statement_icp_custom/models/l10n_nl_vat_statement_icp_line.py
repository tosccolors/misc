# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class VatStatementIcpLine(models.Model):
    _inherit = "l10n.nl.vat.statement.icp.line"

    def _check_country_code(self):
        """Defuse constraint for country codes"""
        pass
