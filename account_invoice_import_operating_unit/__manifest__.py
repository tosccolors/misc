# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Invoice Import OU support",
    "summary": "Set OU on incoming mail servers",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "author": "Hunki Enterprises BV",
    "license": "AGPL-3",
    "depends": [
        "account_invoice_import",
        "operating_unit",
    ],
    "data": [
        "views/operating_unit.xml",
    ],
}
