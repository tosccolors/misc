from odoo import fields, models


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        result["has_multi_edit_security_group"] = self.env.user.has_group('web_tree_multi_edit_security.group_multi_edit')
        return result
