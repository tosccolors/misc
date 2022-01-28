# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    @api.constrains('team_id', 'operating_unit_id')
    def _check_team_operating_unit(self):
        for rec in self:
            if (rec.team_id and rec.team_id.operating_unit_id and
                    rec.team_id.operating_unit_id != rec.operating_unit_id):
                raise ValidationError(_('Configuration error\n'
                                        'The Operating Unit of the sales team '
                                        'must match with that of the '
                                        'quote/sales order'))

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    @api.multi
    @api.constrains('operating_unit_id')
    def _check_sales_order_operating_unit(self):
        pass
