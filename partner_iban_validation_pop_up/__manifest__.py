# -*- coding: utf-8 -*-
{
    'name': "partner_iban_validation_pop_up",

    'summary': """
         Pop-up a message whenever user enters bank account number if not valid IBAN.""",

    'description': """
        Pop-up a message whenever user enters bank account number if not valid IBAN.
    """,

    'author': "Magnus-Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_iban'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}