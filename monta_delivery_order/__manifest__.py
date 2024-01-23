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
    'depends': ['sale_stock', 'partner_firstname', 'purchase_stock', 'base_address_extended',
                'stock_picking_customer_ref', 'delivery', 'stock_move_backdating'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'wizard/monta_product_stock_wizard_view.xml',
        'views/monta_config_view.xml',
        'views/monta_picking_view.xml',
        'views/stock_view.xml',
        'views/res_partner_view.xml',
        'views/monta_stock_lot_view.xml',
        'views/delivery_carrier_view.xml',
        'views/monta_delivery_block_view.xml',
        'views/sale_view.xml',
        'views/menuitem.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'monta_delivery_order/static/src/xml/tree.xml',
            'monta_delivery_order/static/src/js/monta_stock_tree_extend.js',
        ],
    },
}