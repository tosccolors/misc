# -*- coding: utf-8 -*-
{
    'name': "dutch_accounting_localization",

    'summary': """
        Dutch accounting enhancement""",

    'description': """
        Dutch accounting enhancement
    """,

    'author': "Magnus-Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_vat'],

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