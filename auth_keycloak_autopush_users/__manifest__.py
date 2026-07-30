{
    "name": "Auto-Push Users to Keycloak",
    "summary": "Auto-push Portal user to Keycloak",
    "version": "15.0.1.0.0",
    'category': 'Tools',
    'website' : "https://www.tosc.nl/",
    "author": "Deepa, The Open Source company (TOSC)",
    "license": "LGPL-3",
    "depends": [
        "auth_signup",
        "auth_keycloak",
    ],
    "data": [
        "views/auth_oauth.xml",
        "views/res_users.xml",
        "templates/portal.xml",
    ],
}
