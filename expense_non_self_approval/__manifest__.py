# -*- coding: utf-8 -*-
{
    'name': "expense_non_self_approval",

    'summary': """
            This module makes sure that users cannot approve their own expenses if they have the expenses - officer security group'""",

    'description': """
        Prohibit approval of own expenses
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Others',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_expense'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}