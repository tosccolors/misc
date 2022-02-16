# -*- coding: utf-8 -*-
{
    'name': "Consolidation - Group COA mapping",

    'summary': """
        Consolidation - Group COA mapping          
                """,

    'description': """
        Allows you to map an external systems Gl Account, that can be used for grouping/mapping associated COA;
        including an option to capture Trading Partner Reference in Partner.
    """,

    'author'  : "Magnus",
    'website' : "https://www.magnus.nl/",
    'license' : "LGPL-3", 
    'category': 'Accounts',
    'version' : '10.0',
    'depends' : ['account'],
    'data'    : [
                'views/partner_view.xml',
                'views/account_view.xml',
                ],
    'demo'    : [],
}