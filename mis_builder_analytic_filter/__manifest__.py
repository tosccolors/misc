# -*- coding: utf-8 -*-
{
    'name': "MIS Builder Analytic Axis Filter",
    'version': '8.0.1.0.0',
    'category': 'Reporting',
    'summary': """
        Add analytic filters to MIS Reports
    """,
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'license': 'AGPL-3',
    'depends': [
        'mis_builder',
        'operating_unit'
    ],
    'data': [
        'views/mis_report_view.xml',
        'views/mis_builder_analytic.xml',
    ],
    'qweb': [
        'static/src/xml/mis_widget.xml'
    ],
    'installable': False,
}
