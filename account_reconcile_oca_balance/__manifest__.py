# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Balance in reconciliation",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Shows the balance of lines being reconciled",
    "author": "The Open Source Company",
    "website": "http://www.tosc.nl",
    "category": "Accounting & Finance",
    "depends": [
        "account_reconcile_oca",
    ],
    "installable": True,
    "data": [
        "views/account_account_reconcile.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "account_reconcile_oca_balance/static/src/scss/account_reconcile_oca_balance.scss",
        ],
    },
}
