# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright 2015 Magnus
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, exceptions, models, _
from odoo.exceptions import UserError, ValidationError



class ResPartner(models.Model):
    """
    Add field to determine wether a supplier is a default supplier for
    fetchmail invoice.
    Validations:
        if fetchmail_invoice_default is True:
            - partner must be a supplier
            - There can only be one partner per company with this attribute
    """
    _inherit = 'res.partner'

    default_supplier = fields.Boolean(string='Default (Dummy) Supplier',
                                      help='Will be used as default partner when invoices are'
                                           'created from batch import')

    @api.constrains('default_supplier')
    def constrains_default_supplier(self):
        for rec in self.filtered("default_supplier"):
            if rec.default_supplier:
                if not rec.supplier:
                    raise UserError(_('Default Supplier must be a supplier'))
            # Check wether not another partner on same company default
            company_id = (rec.company_id and rec.company_id.id or False)
            if company_id:
                args = [('default_supplier', '=', True),
                        ('id', '!=', rec.id),
                        ('company_id', '=', company_id), ]
                other_ids = self.search(args)
                if other_ids:
                    raise UserError(_('There can only be one default supplier per company'))
            else:
                raise UserError(_('a default supplier has to have a company defined'))

        # If we get here, validation passed, only use exceptions for errors.
        return True



