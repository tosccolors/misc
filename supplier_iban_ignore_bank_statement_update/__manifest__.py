# -*- coding: utf-8 -*-
{
    'name': "supplier_iban_ignore_bank_statement_update",

    'summary': """
        The IBAN should not update for supplier while updating bank statement.""",

    'description': """
        The IBAN should not update for supplier while updating bank statement.
    """,

    'author': "TOSC-Sushma",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

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