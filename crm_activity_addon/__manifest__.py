# -*- coding: utf-8 -*-
{
    'name': "crm_activity_addon",

    'summary': """
        crm_activity_addon""",

    'description': """
        crm_activity_addon
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Others',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/crm_activity_log_views.xml',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'external_dependencies': {
        'python': ['bs4'],
    },
}