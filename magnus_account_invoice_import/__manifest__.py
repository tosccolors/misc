# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Invoice Import (Magnus customizations)",
    "summary": "Use a machine learning model to parse invoices",
    "version": "10.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Hunki Enterprises BV",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_import_ml",
        "account_operating_unit",
    ],
    "data": [
        "views/account_invoice.xml",
        "views/operating_unit.xml",
    ],
}
