# -*- coding: utf-8 -*-
{
    'name': "Customer IAOC",

    'summary': """
        This module makes sure that sales users can modify customer fields that are relevant for sales, but are normally positioned at the finance tab.  
    """,

    'description': """
        This module makes sure that sales users can modify customer fields that are relevant for sales, but are normally positioned at the finance tab.
    """,

    'author': "TOSC - DK",
    'website': "http://www.tosc.nl",

    'category': 'Others',
    'version': '0.1',
    'depends': ['base_vat','account_invoice_transmit_method','account_payment_partner'],

    'data': [
        'views/res_partner_view.xml',
    ],
}
