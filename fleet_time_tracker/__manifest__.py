# -*- coding: utf-8 -*-
{
    'name': "fleet_time_tracker",

    'summary': """
            Fleet time tracker
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
    'depends': ['data_time_tracker', 'fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/fleet_vehicle_view.xml',
        'views/res_partner_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}