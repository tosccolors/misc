from odoo.addons.l10n_nl_xaf_auditfile_export import tests as base_tests


class TestNlXafAuditfileExport(base_tests.test_l10n_nl_xaf_auditfile_export.TestXafAuditfileExport):
    def setUp(self):
        super().setUp()
        self.ou = self.env.ref('operating_unit.main_operating_unit')
        self.env = self.env(context=dict(self.env.context, default_operating_unit_id=self.ou.id))
