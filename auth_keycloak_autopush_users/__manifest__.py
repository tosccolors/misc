# -*- coding: utf-8 -*-


{
    "name": "Auto-Push Users to Keycloak",
    "summary": "Autopushing of Portal user to Keycloak",
    "version": "14.0.3.0",
    'category': 'Tools',
    'website' : "https://www.tosc.nl/",
    "author": "Deepa, " "The Open Source company (TOSC)",
    "depends": [
        "auth_signup",
        "auth_keycloak",
    ],
    "data": [
        "views/res_users.xml",
        "views/auth_oauth.xml"
    ],
}
