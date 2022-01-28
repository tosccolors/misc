# -*- coding: utf-8 -*-
# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Operating Unit Report Layout",

    'summary': "This module creates basic layouts for reports.",

    'description': """
        This module creates a basic paperformat (id: paperformat_ou_layout) and image fields (logo, report_background_image1) in operating unit.\n
        Usage:\n
        To extend/inherit this module please add this module name in the dependency list of your module.\n
        To extend/inherit the basic paperformat please use the module name and the id (Ex: <record id="operating_unit_report_layout.paperformat_ou_layout" model="report.paperformat">).\n
        To use this paperformat please mention the module name and the id (Ex: <report paperformat="operating_unit_report_layout.paperformat_ou_layout" />).\n

    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'accounts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'operating_unit'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/operating_unit_view.xml',
        # 'views/templates.xml',
        'report/report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
