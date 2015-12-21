{
    'name': 'Scrollable list view',
    'version': '1.0.0',
    'sequence': 150,
    'category': 'Anybox',
    'description': """
         Once you install this module, you won't need to scroll up to find your menus!

         the openERP/Odoo listview style will take care the page browser height
         and make the listview scrollable (not the page anymore).
    """,
    'author': 'Anybox',
    'website': 'http://anybox.fr',
    'depends': [
        'base',
        'web',
    ],
    'js': [
        'static/src/js/listview.js',
    ],
    'qweb': [
    ],
    'css': [
        'static/src/css/listview.css',
        'static/src/css/leftbar.css',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
