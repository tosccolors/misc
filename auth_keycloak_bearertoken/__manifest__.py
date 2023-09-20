# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'OAuth2 Authentication - Keycloak',
    'category': 'Tools',
    'version': '10.1',
    'maintainer': 'TOSC',
    'depends': ['base', 'web', 'base_setup', 'auth_signup','auth_oauth'],
    'data': [
        'views/auth_oauth_views.xml',
    ],
}
