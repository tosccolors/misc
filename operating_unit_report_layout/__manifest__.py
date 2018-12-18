# -*- coding: utf-8 -*-
# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "Operating Unit Report Layout",

    'summary': "This module creates basic layouts for reports.",

    'description': """
        This module creates a basic external layout (external_layout_ou) and a paperformat (paperformat_ou_layout).\n
        Usage:\n
        To extend/inherit the basic external layout please use the module name and the id (Ex: <t t-call="operating_unit_report_layout.external_layout_ou" />).\n
        To extend/inherit the basic paperformat please use the module name and the id (Ex: <report paperformat="operating_unit_report_layout.paperformat_ou_layout" />).\n

    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'accounts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
        # 'views/templates.xml',
        'report/report.xml',
        'report/report_invoice.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
