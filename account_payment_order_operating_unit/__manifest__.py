# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Account Payment Order Operating Unit',
    'version': '14.0.1.0.0',
    'license': 'AGPL-3',
    "author": "The Open Source Company",
    'category': 'Banking addons',
    'depends': [
        'account_payment_order',
        'account_operating_unit',
    ],
    'data': [
        'security/account_payment_order_operating_unit.xml',
        'views/account_payment_order.xml',
    ],
    'demo': [
    ],
    'installable': True,
}
