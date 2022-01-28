# -*- coding: utf-8 -*-
{
    'name': 'Mass Mail Invoice',
    'summary': 'This module allows sending massive emails of invoices to customers.',
    'category': 'Accounting',
    'version': '1.0',
    'website': 'http://www.magnus.nl',
    'author': 'Magnus - Willem Hulshof',
    'depends': [
        'account_invoice_transmit_method',
        'base_report_to_printer'
        ],
    'data': [
        "views/mass_mail_view.xml",
        "views/account_invoice_view.xml",
        "views/partner.xml"
    ],
    'installable': True
}
