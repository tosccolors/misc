{
    "name": 'Default account for analytic policy "always"',
    "summary": "Set default account for account types with analytic policy 'always'",
    "version": "14.0.1.0.0",
    "website": "http://www.tosc.nl",
    "author": "The Open Source Company",
    "depends": [
        'account_analytic_required',
    ],
    "data": [
        "views/account_account_type.xml",
    ],
    'installable': True,
}
