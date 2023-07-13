# -*- coding: utf-8 -*-


{
    "name": "Disable Odoo Password & Auto-Push Users to Keycloak",
    "summary": "Disable Password in Login Page, Autopushing of Portal user to Keycloak",
    "version": "14.0.1.0.0",
    'category': 'Tools',
    'website' : "https://www.tosc.nl/",
    "author": "Deepa, " "The Open Source company (TOSC)",
    "depends": [
        "auth_signup",
        "auth_keycloak",
    ],
    "data": [
        "views/res_users.xml"
    ],
}
