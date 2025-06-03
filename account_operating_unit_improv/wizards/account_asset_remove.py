from odoo import models


class AccountAssetRemove(models.TransientModel):
    _inherit = "account.asset.remove"

    def _get_removal_data(self, asset, residual_value):
        result = super()._get_removal_data(asset, residual_value)
        for _, _, vals in result:
            vals['operating_unit_id'] = asset.operating_unit_id.id
        return result
