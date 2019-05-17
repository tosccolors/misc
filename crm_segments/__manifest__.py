# -*- coding: utf-8 -*-
{
    'name': "crm_segments",

    'summary': """
        This module adds 4 segments to the res.partner object, to be configured in the Sales > Configuration menu. These segments can be used for various purposes, for example defining customer segments in order to do sales reporting based on these segments. Segment fields will be copied to sale orders.
    """,

    'description': """
        This module adds 4 segments to the res.partner object, to be configured in the Sales > Configuration menu. These segments can be used for various purposes, for example defining customer segments in order to do sales reporting based on these segments. Segment fields will be copied to sale orders.
    """,

    'author': "Magnus - DK",
    'website': "http://www.yourcompany.com",

    'category': 'Others',
    'version': '0.1',
    'depends': ['sale','crm','sales_team'],

    'data': [
        'security/ir.model.access.csv',
        'views/crm_segments_view.xml',
        'views/res_partner_view.xml',
    ],
}
