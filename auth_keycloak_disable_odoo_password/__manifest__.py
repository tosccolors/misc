# -*- coding: utf-8 -*-


{
    "name": "Odoo Disable Password",
    "summary": "Disable Password in Login Page",
    "version": "10.0.1.2.0",
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
