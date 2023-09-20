# -*- coding: utf-8 -*-
{
    'name': "oca_report_operating_unit",

    'summary': """
        Additional filter on oca reporting module.
        """,

    'description': """
        Additional filter on oca reporting module.
    """,

    'author'  : 'Eurogroup Consulting - Willem Hulshof',
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_financial_report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/general_ledger_wizard_view.xml',
        'wizard/journal_report_wizard_view.xml',
        'wizard/trial_balance_wizard_view.xml',
        'wizard/open_items_wizard_view.xml',
        'wizard/aged_partner_balance_wizard_view.xml',
        'report/templates/general_ledger.xml',
        'report/templates/journal.xml',
        'report/templates/trial_balance.xml',
        'report/templates/open_items.xml',
        'report/templates/aged_partner_balance.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
