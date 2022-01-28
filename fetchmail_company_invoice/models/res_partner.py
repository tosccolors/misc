# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    This module copyright (c) 2013 Therp BV <http://therp.nl>
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

from odoo import _, api, fields, models
from odoo.exceptions import UserError, RedirectWarning, ValidationError

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

    fetchmail_invoice_default = fields.Boolean('Default invoice partner', help='Will be used as default partner when invoices are'
            'created from received mails')

    @api.constrains('fetchmail_invoice_default')
    def _check_fetchmail_invoice_default(self):
        for this_obj in self:
            if this_obj.fetchmail_invoice_default:
                if not this_obj.supplier:
                    raise ValidationError(_('Default invoice partner must be a supplier'))

                # Check wether not another partner on same company default
                company_id = (
                    this_obj.company_id and this_obj.company_id.id or False)
                if company_id:
                    args = [('fetchmail_invoice_default', '=', True),
                        ('id', '!=', this_obj.id),
                        ('company_id', '=', company_id),]
                    other_ids = self.search(cr, uid, args)
                    if other_ids:
                        raise ValidationError(_('There can only be one default supplier per company'))

                else:
                    raise ValidationError(_('a default supplier has to have a company defined'))

        # If we get here, validation passed, only use exceptions for errors.
        return True



