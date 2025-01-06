# -*- encoding: utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2022-present TOSC (<http://www.tosc.nl>). All Rights Reserved
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
    'name': "Supplier Bank Account Approval",

    'summary': """
        Supplier Bank Account Approval""",

    'description': """
        \n1.Add state draft and confirmed to the banks_account_ids from partner.
        \nThis should only apply to partners is supplier = true
        \n2.New menu called 'Sensitive fields approval' where any changes can be approved. 
        \nThis menu should only be visible and available to new security group 'Bank Account Manager'
        \n3.When a bank account is changed or added, it will be in draft state. It cannot be used in any invoice or payment.
        \nwhen creating an invoice or payment which says that "The supplier has changed bank details which are not yet approved.
        """,

    'author': "TOSC-Sify, Deepa Venkatesh (DK), The Open Source Company (TOSC)",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '16.0.3.0',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_payment_order', 'partner_manual_rank'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [],
    'license': 'LGPL-3',
}