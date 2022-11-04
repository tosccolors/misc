# -*- coding: utf-8 -*-
{
    'name': "Expense Payment Order Check",

    'summary': """
        Payment Order Preview on Expense Report""",

    'description': """
        Module that allows the users to check the Expense Report that are part of a payment order.
    """,

    'author': "K.Sushma",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/payment_security.xml',
        'views/hr_expense_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}