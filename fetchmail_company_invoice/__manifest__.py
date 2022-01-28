# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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

{
    "name": "Link an incoming mail (fetchmail) configuration to a company",
    "description": """\
OpenERP gives the possibility to automatically create documents (like leads or
invoices) for mails retrieved.

A lot of documents in the system are tied to specific companies. This module
makes it possible to link a fetchmail configuration document to a specific
company, so this can be used in the documents created.

See also https://bugs.launchpad.net/therp-addons/+bug/1219418

This module is compatible with OpenERP 7.0.
""",
    "category": "Server Tools",
    "version": "7.1.r083",
    "author": "Therp BV",
    "website": 'http://therp.nl',
    "depends": ['fetchmail', 'account'],
    "update_xml": [
        'views/fetchmail_server_view.xml',
        'views/res_partner_view.xml',
        ],
    "js": [],
    "qweb": [],
    "css": [],
    'installable': True,
    'active': False,
}
