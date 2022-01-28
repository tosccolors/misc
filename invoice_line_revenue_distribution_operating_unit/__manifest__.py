# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "Revenue Distribution per Invoice Line and Operating Unit",

    'summary': """
        This module facilitates splitting revenue to different Operating Units by
        allowing different OU's on the invoice lines. """,

    'description': """
        This module facilitates splitting revenue to different Operating Units by
        allowing different OU's on the invoice lines and having another OU in the header, so accounts payable 
        and tax is in another OU from the revenue lines. The automatic clearance journal entry will take place 
        at confirmation of the invoice.
    """,

    'author': "Magnus",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting & Finance',
    'version': '10.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': ['sale','account_operating_unit','analytic_operating_unit'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
#        'demo/demo.xml',
    ],
}