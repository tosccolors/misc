# -*- coding: utf-8 -*-
{
    'name': 'MIS Builder Operating Unit',
    'version': '10.0',
    'category': 'Reporting',
    'summary': """
        Build 'Management Information System' Reports and Dashboards - extends with Operating Units
    """,
    'author': 'Magnus - Willem Hulshof',
    'website': 'http://www.magnus.nl',
    'depends': [
        'mis_builder',
        'operating_unit',
    ],
    'data': [
        'views/account_view.xml',
        'views/mis_report_view.xml'
    ],
    'installable': False,
    'application': True,
    'license': 'AGPL-3',
}
