# -*- coding: utf-8 -*-
{
    "name": 'WriteOff with Operating Units',
    "summary": "Introduces Operating Unit fields in writeoff wizard",
    "version": "10.0.1.1.0",
    'author': "TOSC-Sushma",
    'website': "http://www.tosc.nl",
    "category": "Accounting & Finance",
    "depends": ['account_operating_unit'],
    "data": [
        # "wizard/account_reconcile_view.xml",
        # reconcile model is removed in odoo12
    ],
    'qweb': [
       "static/src/xml/account_reconciliation.xml",
        ],
    'installable': True,
}