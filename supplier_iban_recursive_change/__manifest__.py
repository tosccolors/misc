# -*- coding: utf-8 -*-
{
    'name': "supplier_iban_recursive_change",

    'summary': """
        Update vendor bills and payment orders, if new standard  IBAN is added to a supplier.
        """,

    'description': """
        Update vendor bills and payment orders, if new standard  IBAN is added to a supplier.
    """,

    'author': "Magnus-Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}