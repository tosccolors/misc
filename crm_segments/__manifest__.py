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
    'name': "CRM Segments",

    'summary': """
        This module adds 4 segments to the res.partner object, to be configured in the Sales > Configuration menu. 
            """,

    'description': """
        This module adds 4 segments to the res.partner object, to be configured in the Sales > Configuration menu. These segments can be used for various purposes, for example defining customer segments in order to do sales reporting based on these segments. Segment fields will be copied to sale orders.
    """,

    'author': "Deepa Venkatesh (DK), " "Willem Hulsof, The Open Source Company (TOSC)",
    'website': 'http://www.tosc.nl',

    'category': 'Others',
    'version': '16.0.0',
    'depends': ['sale'],

    'data': [
        'security/crm_segment_security.xml',
        'security/ir.model.access.csv',

        'views/crm_segments_views.xml',
        'views/res_partner_view.xml',
    ],
}
