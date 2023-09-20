# -*- coding: utf-8 -*-
{
    'name': "Invoice Duplication Bank Account Check",

    'summary': """
        Modify Duplicate functionality of invoices""",

    'description': """
       \n 1. When duplicating an invoice, check if the back account from the original 
       \n invoice is linked to the res.partner of the original invoice.
        \n 2.When validating the invoice, check again if the back account 
        \n is linked to the res.partner
    """,

    'author': "TOSC-Sify",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}