# -*- coding: utf-8 -*-
{
    'name': "accounting_source_document_attachment_preview",

    'summary': """
        This module allows you to directly preview the attachment of a source document from a journal entry.
        """,

    'description': """
        This module allows you to directly preview the attachment of a source document from a journal entry.
        """,

    'author': "K.Sushma",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Knowledge Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['attachment_preview', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/ir_attachment_views.xml',
        'views/templates.xml',
    ],
    'qweb': [
        "static/src/xml/qweb.xml",
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}