# -*- coding: utf-8 -*-
{
    'name': "account_cutoff_accrual_no_taxes",

    'summary': """
        account cutoff accrual no taxes""",

    'description': """
        account cutoff accrual no taxes
    """,

    'author': "K.Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_cutoff_accrual_dates'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_config_settings.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}