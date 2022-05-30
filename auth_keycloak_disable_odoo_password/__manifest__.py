# -*- coding: utf-8 -*-


{
    "name": "Keycloak Odoo Disable Password",
    "summary": "Disable Password in Login Page, Autopushing of Portal user to Keycloak, which inturn will send password mails to user",
    "version": "10.0.1.3.0",
    'category': 'Tools',
    'website' : "https://www.magnus.nl/",
    'author': 'Magnus Red',
    "depends": [
        "auth_keycloak",
    ],
    "data": [
        "views/res_users.xml"
    ],
}
