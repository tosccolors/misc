# -*- coding: utf-8 -*-
{
    "name": 'WriteOff with Operating Units',
    "summary": "Introduces Operating Unit fields in writeoff wizard",
    "version": "10.0.1.1.0",
    'author': "Magnus-Sushma",
    'website': "http://www.magnus.nl",
    "category": "Accounting & Finance",
    "depends": ['account_operating_unit'],
    "data": [
        "wizard/account_reconcile_view.xml",
    ],
    'qweb': [
       "static/src/xml/account_reconciliation.xml",
        ],
    'installable': True,
}