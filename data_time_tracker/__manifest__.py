# -*- coding: utf-8 -*-
{
    'name': "Data-Time Tracker",

    'summary': """
        This is a generic module which can be used on any object.
        In this module, user can track object's data changes for specific time period.    
    """,

    'description': """
        
    """,

    'author': "Magnus - Willem Hulshof",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Others',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/tracker_wizard_view.xml',
        'views/data_time_tracking_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
