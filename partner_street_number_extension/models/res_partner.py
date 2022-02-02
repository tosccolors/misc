# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, an open source suite of business apps
#    This module copyright (C) 2013-2015 Therp BV (<http://therp.nl>).
#
#    @authors: Stefan Rijnhart, Ronald Portier
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

import re
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    @api.depends('street_name', 'street_number', 'street_number_extension')
    def _get_street(self):
        for partner in self:
            partner.street = ' '.join(
                filter(None, [partner.street_name, partner.street_number, partner.street_number_extension]))

    def _write_street(self):
        """
        Simplistically try to parse in case a value should get written
        to the 'street' field (for instance at import time, which provides
        us with a way of easily restoring the data when this module is
        installed on a database that already contains addresses).
        """
        for partner in self:
            street_name = partner.street.strip() if partner.street else False
            street_number = False
            street_number_extension =False
            if street_name:
                match = re.search(r'(.+)\s+(\d.*)\s+(.+)', street_name)
                if match and len(match.group(2)) < 6:
                    street_name = match.group(1)
                    street_number = match.group(2)
                    street_number_extension = match.group(3)
            partner.street_name = street_name
            partner.street_number = street_number
            partner.street_number_extension = street_number_extension

    @api.model
    def _address_fields(self):
        """
        Pass on the fields for address synchronisation to contacts.

        This method is used on at least two occassions:

        [1] when address fields are synced to contacts, and
        [2] when addresses are formatted

        We want to prevent the 'street' field to be passed in the
        first case, as it has a fallback write method which should
        not be triggered in this case, while leaving the field in
        in the second case. Therefore, we remove the field
        name from the list of address fields unless we find the context
        key that this module injects when formatting an address.

        Could have checked for the occurrence of the synchronisation
        method instead, leaving the field in by default but that could
        lead to silent data corruption should the synchronisation API
        ever change.
        """
        res = super(ResPartner, self)._address_fields()
        return res + ['street_number_extension']

    street_number_extension = fields.Char(
        'Street number extension'
    )
