# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Sale(models.Model):
    _inherit = 'sale.order'

    @api.onchange('commitment_date')
    def _check_commitment_date(self):
        if self.commitment_date and self.commitment_date.date() <= fields.Datetime.now().date():
            raise ValidationError(
                _("Delivery date must be future date!")
            )

    def action_confirm(self):
        if (self.commitment_date and self.commitment_date.date() <= fields.Datetime.now().date())\
                or not self.commitment_date:
            raise ValidationError(
                _("Delivery date must be future date OR cannot be empty!")
            )
        return super().action_confirm()
