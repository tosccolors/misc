# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Sent date for invoices",
    'summary': "Adds field sent_date to invoices",
    'author': "TOSC",
    'website': "http://www.tosc.nl",
    "category": "Accounting/Accounting",
    'version': '16.0.1.0.0',
    'depends': ['account_invoice_transmit_method'],
    'data': ['views/account_move.xml'],
    'post_init_hook': 'post_init_hook',
}
