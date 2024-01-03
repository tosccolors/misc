# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "BI SQL Excel Reports",
    "summary": "Pull SQL reports defined in Odoo from within Excel, using the Excel add-in and this module",
    "version": "10.0.1.0.0",
    "author": "Magnus",
    "website": "https://www.magnus.nl/",
    "license": "AGPL-3",
    "category": "Reporting",
    "depends": [
        'bi_sql_editor',
        'decimal_precision',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/view_bi_sql_excel_report.xml',
        'views/view_bi_sql_view.xml',
        'views/view_board_download.xml',
        'wizard/bi_sql_excel_report_get_addin_view.xml',
    ],
    'installable': True,
    'external_dependencies': {
        'python': [
        ],
    },
}
