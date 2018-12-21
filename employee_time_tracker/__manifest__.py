# -*- coding: utf-8 -*-
{
    'name': "employee_time_tracker",

    'summary': """
            Enables time dependent relation between hr employee and hr department
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
        'depends': ['data_time_tracker', 'hr'],

        # always loaded
        'data': [
            # 'security/ir.model.access.csv',
            'views/hr_department_view.xml',
            'views/hr_employee_view.xml',
        ],
        # only loaded in demonstration mode
        'demo': [
            # 'demo/demo.xml',
        ],
    }