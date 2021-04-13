# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Invoice Import with Machine Learning",
    "summary": "Use a machine learning model to parse invoices",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/edi",
    "author": "Hunki Enterprises BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_import",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "data/product_product.xml",
        "data/res_partner.xml",
        "views/account_invoice.xml",
        "views/res_partner.xml",
        "views/templates.xml",
    ],
    "qweb": [
        "static/src/xml/account_invoice_import_ml.xml",
    ]
}
