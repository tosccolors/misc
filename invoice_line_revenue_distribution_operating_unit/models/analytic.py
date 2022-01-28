# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    linked_operating_unit = fields.Boolean('Linked Operating Unit')

    @api.multi
    @api.constrains('operating_unit_ids', 'linked_operating_unit')
    def _check_length_operating_units(self):
        for aa in self:
            if (
                    aa.linked_operating_unit and
                    len(aa.operating_unit_ids) != 1
            ):
                raise ValidationError(_('Fill in one and only one Operating Unit. '
                                        'move lines with this analytic account '
                                        'will also have the linked Operating Unit.'))
        return True


