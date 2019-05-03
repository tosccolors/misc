# -*- coding: utf-8 -*-
{
    'name': "Customer IAOC",

    'summary': """
        This module makes sure that sales users can modify customer fields that are relevant for sales, but are normally positioned at the finance tab  
    """,

    'description': """
        This module makes sure that sales users can modify customer fields that are relevant for sales, but are normally positioned at the finance tab
    """,

    'author': "Magnus - DK",
    'website': "http://www.yourcompany.com",

    'category': 'Others',
    'version': '0.1',

    'depends': ['account_invoice_transmit_method','base_vat'],

    'data': [
        'views/res_partner_view.xml',
    ],
}
