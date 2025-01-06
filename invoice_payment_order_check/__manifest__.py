# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2022 Magnus (<http://www.magnus.nl>). All Rights Reserved
#    Copyright (C) 2022-2024 TOSC (<http://www.tosc.nl>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Invoice Payment Order Check",

    'summary': """
        Payment Order Preview on Invoice""",

    'description': """
        Module that allows the users to check the invoices that are part of a payment order.

    """,

    'author': "K.Sushma, Deepa Venkatesh (DK), The Open Source Company (TOSC)",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '16.0.2.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_payment_order'],

    # always loaded
    'data': [
        'security/payment_security.xml',
        'views/invoice_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'LGPL-3',
}