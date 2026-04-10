{
    'name': "Tier validation: Expand reviews dropdown by default",
    'summary': "Show the reviews dropdown in open state by default",
    'author': "The Open Source Company (TOSC)",
    'website': "https://tosc.nl",
    'category': 'Tools',
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    'depends': ['base_tier_validation'],
    "assets": {
        "web.assets_backend": [
            "/base_tier_validation_expand_reviews/static/src/xml/tier_review_template.xml",
        ],
    },
}
