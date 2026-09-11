{
    'name': "Supplier Bank Account Approval",
    'summary': "Supplier Bank Account Approval",
    'author': "TOSC",
    'website': "http://www.tosc.nl",
    'category': 'Uncategorized',
    'version': '14.0.1.0.0',
    'depends': ['base','account','account_payment_order'],
    'data': [
        'security/supplier_bank_change_approval.xml',
        'views/res_partner_bank.xml',
        'views/account_move.xml',
        'views/account_payment_line.xml',
        'views/menu.xml',
    ],
}
