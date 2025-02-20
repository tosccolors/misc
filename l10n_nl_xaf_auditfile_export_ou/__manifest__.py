# Copyright 2025 The Open Source company
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "XAF auditfile export (Operating Unit)",
    "version": "14.0.0.0.0",
    "author": "Deepa Venkatesh (DK), The Open Source Company (TOSC)",
    "website": 'http://www.tosc.nl',
    "license": "AGPL-3",
    "category": "Localization/Netherlands",
    "summary": "Export XAF auditfiles for Dutch tax authorities, extended further to consider Operating Unit",
    "depends": ["l10n_nl_xaf_auditfile_export",'account_operating_unit','partner_coc'],
    "data": [
        "views/xaf_auditfile_export.xml",
        "views/templates.xml",
    ],
    "installable": True,
}
