{
    'name': "Tree multi edit security",
    'summary': "Restrict the multi edit feature of list views to a security group",
    'author': "The Open Source Company (TOSC)",
    'website': "https://tosc.nl",
    'category': 'Tools',
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    'depends': ['web'],
    "data": [
        "security/web_tree_multi_edit_security.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "web_tree_multi_edit_security/static/src/js/list_view.esm.js",
        ],
    }
}
