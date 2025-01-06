{
    'name': 'Account Migration Remarks',
    'version': '16.0.1.0.0',
    'summary': 'Add migration remarks field to account move',
    'description': 'This module adds a new text field called "Migration Remarks" to the account.move model, displayed on the Other Info tab of the form view.',
    'category': 'Accounting',
    'author': 'The Open Source Company',
    'depends': ['account'],
    'data': [
        'views/account_move_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}