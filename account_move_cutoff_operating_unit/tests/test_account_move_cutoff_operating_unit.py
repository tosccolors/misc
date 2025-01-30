# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests import tagged
from odoo.addons.account_move_cutoff.tests import test_account_invoice_cutoff


@tagged("-at_install", "post_install")
class TestAccountMoveCutoffOperatingUnit(test_account_invoice_cutoff.TestInvoiceCutoff):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ou = cls.env.ref('operating_unit.b2c_operating_unit')
        cls.invoice.operating_unit_id = cls.ou
        cls.invoice.line_ids.write({
            'operating_unit_id': cls.ou.id,
        })

    def test_account_invoice_cutoff_equals(self):
        super().test_account_invoice_cutoff_equals()
        self.assertEqual(self.invoice.cutoff_entry_ids.operating_unit_id, self.ou)
        self.assertEqual(self.invoice.cutoff_entry_ids.line_ids.operating_unit_id, self.ou)
