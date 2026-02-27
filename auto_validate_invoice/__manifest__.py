# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2025-present The Open Source Company (<http://www.tosc.nl>). All Rights Reserved
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
    'name': 'Auto Validate Invoices',
    'version': '14.0.4.0',
    'category': 'Invoice',
    'description': """
This module automatically validates draft Invoices with the help of Cron.
============================================================================================


    """,
    'author': 'Deepa Venkatesh (DK), The Open Source Company (TOSC)',
    'website': 'http://www.tosc.nl',
    'depends': [
                'account', 'account_invoice_transmit_method',
                ],
    'data': [
             "data/ir_cron.xml",
             "data/transmit_method.xml",

            "views/account_invoice_views.xml"
             ],
    'qweb': [
    ],
    'demo': [],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

