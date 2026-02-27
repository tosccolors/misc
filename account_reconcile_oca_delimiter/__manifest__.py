# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Custom delimiter in bank statement matching",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "summary": "Allows to set additional delimiters for tokenization of bank statement strings",
    "author": "The Open Source Company",
    "website": "http://www.tosc.nl",
    "category": "Accounting & Finance",
    "depends": [
        "account_reconcile_oca",
    ],
    "installable": True,
    "data": [
        "views/account_reconcile_model.xml",
    ],
}
