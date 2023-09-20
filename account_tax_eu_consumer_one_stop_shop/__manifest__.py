# -*- coding: utf-8 -*-
# © 2021 Magnus (Willem Hulshof <w.hulshof@magnus.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account EU Consumer tax onestopshop',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'tax configuration for inter-EU consumer trade and the one stop shop tax ....',
    'author': 'TOSC',
    'website': 'http://www.tosc.nl',
    'depends': [
        'account', 'sale'
        ],
    'data': [
        'views/product.xml',
        'views/account_fiscal_position.xml',
        'views/account_tax.xml'
    ],
    'images': [
        ],
    'installable': True,
}
