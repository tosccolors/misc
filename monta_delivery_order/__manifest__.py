# -*- coding: utf-8 -*-
{
    'name': "monta_delivery_order",

    'summary': """
        We require a interface between Odoo and a logistical system called 'Monta Portal'. The purpose of this interface is to reflect outgoing and incoming stock movements between Odoo and Monta Portal.""",

    'description': """
        We require a interface between Odoo and a logistical system called 'Monta Portal'. The purpose of this interface is to reflect outgoing and incoming stock movements between Odoo and Monta Portal.
    """,

    'author': "K.Sushma",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_stock', 'partner_firstname'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/monta_config_view.xml',
        'views/monta_picking_view.xml',
        'views/stock_view.xml',
        'views/menuitem.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}