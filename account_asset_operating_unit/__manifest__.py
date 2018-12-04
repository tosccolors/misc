# -*- coding: utf-8 -*-
# Copyright 2018 Willem Hulshof Magnus (www.magnus.nl).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "account_asset_operating_unit",

    'summary': "Links account_asset and operating_unit.",

    'description': """
This module creates a relation between account.asset.asset and operating.unit models.\n
This is a many2one relation field operating_unit_id in account.asset.asset model (one operating unit has multiple assets but each asset only has one operating unit).\n
On invoice validation the operating_unit_id is copied to account.asset.asset from account.invoice.line.\n
    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_asset', 'operating_unit', 'account_operating_unit'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset_views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable': True
}