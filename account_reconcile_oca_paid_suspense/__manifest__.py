# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Mark paid to suspense account",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Adds a button to mark partially paid invoices as fully paid, assigning the difference to the suspense account",
    "author": "The Open Source Company",
    "website": "http://www.tosc.nl",
    "category": "Accounting & Finance",
    "depends": [
        "account_reconcile_oca",
    ],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "account_reconcile_oca_paid_suspense/static/src/xml/account_reconcile_oca_paid_suspense.xml",
            "account_reconcile_oca_paid_suspense/static/src/js/account_reconcile_oca_paid_suspense.esm.js",
        ],
    },
}
