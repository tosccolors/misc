# -*- coding: utf-8 -*-
{
    'name': "Account Reversal Sql/Job Queue",

    'summary': """
         perform the reversal via a SQL query OR Job Queue""",

    'description': """
       \n Create a new boolean field 'reversal via SQL' in the configuration form view.
       \n If this boolean is false, use the existing ORM methods for reversal
       \n If this boolean is true, perform the reversal via a SQL query
    """,

    'author': "Magnus-Sify",
    'website': 'http://www.magnus.nl',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_reversal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}