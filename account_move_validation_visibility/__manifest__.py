{
    'name': "Move validator",
    'summary': "Adds group move validator who can validate moves without further access to finance",
    'author': "The Open Source Company (TOSC)",
    'website': "https://tosc.nl",
    'category': 'Tools',
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    'depends': ['account_move_tier_validation', 'base_tier_validation_formula'],
    'demo': [
        'demo/res_users.xml',
    ],
    'data': [
        'security/account_move_validation_visibility.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'views/menu.xml',
    ],
}
