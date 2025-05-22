# -*- coding: utf-8 -*-
{
    'name': "purchase_order_extended",

    'summary': """
        Purchase Order Extended""",

    'description': """
        Purchase Order Extended
    """,

    'author': "K.Sushma-TOSC",
    'website': "https://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '16.0.2.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase_stock', 'stock', 'stock_account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_views.xml',
        'views/stock_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
