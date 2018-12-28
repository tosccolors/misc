# -*- coding: utf-8 -*-
{
    'name': "contract_registry",

    'summary': """
        This module is a registry of contracts from the company with its 
        business partners, monitoring renewal/ending etc.""",

    'description': """
        This module is a registry of contracts from the company with its 
        business partners, monitoring renewal/ending etc. The digital(ized)
        actual signed (paper) contract can be attached. Besides a history of
        start-, renewal- and end dates, the object has a description and 
        links to the company_id/operating_unit_id and the relevant business 
        partner(s).
    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo/demo.xml',
    ],
}