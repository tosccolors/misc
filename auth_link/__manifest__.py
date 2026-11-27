{
    'name': "Authenticate via link",
    'summary': "Generate links that log in a user immediately",
    'author': "The Open Source Company (TOSC)",
    'website': "https://tosc.nl",
    'category': 'Tools',
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    'depends': ['web', 'web_ir_actions_act_window_message'],
    'data': [
        "data/ir_actions_server.xml",
        'security/ir.model.access.csv',
        'views/templates.xml',
    ],
}
