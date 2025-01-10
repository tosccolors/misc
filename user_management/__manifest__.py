# -*- coding: utf-8 -*-
{
    'name': "user_management",

    'summary': """
       This group should provide access to the following menu items:

Settings
Settings / Users & Companies
Settings / Users & Companies / Users (only to this sub-menu, not to other sub-menus)
In case of a Keycloak setup, the group should enable pushing to Keycloak (or not block this).

This group should enable the creation of a new user, only allowing changes in the following tabs in the user object:

Roles
Preferences
""",

    'description': """
        This group should provide access to the following menu items:

Settings
Settings / Users & Companies
Settings / Users & Companies / Users (only to this sub-menu, not to other sub-menus)
In case of a Keycloak setup, the group should enable pushing to Keycloak (or not block this).

This group should enable the creation of a new user, only allowing changes in the following tabs in the user object:

Roles
Preferences

    """,

    'author': "K.Sushma TOSC",
    'website': "https://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base_user_role', 'auth_totp'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menuitems.xml',
        'views/res_users_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
