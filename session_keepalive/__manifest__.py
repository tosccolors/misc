{
    'name': "Session keepalive",
    'summary': "Keep session of OIDC procy alive",
    'author': "The Open Source Company (TOSC)",
    'website': "https://tosc.nl",
    'category': 'Tools',
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    'depends': ['auth_oauth'],
    "data": [
        "data/ir_config_parameter.xml",
        "views/res_config_settings.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/session_keepalive/static/src/js/session_keepalive.esm.js",
        ],
    }
}
