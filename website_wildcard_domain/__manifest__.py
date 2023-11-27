# -*- coding: utf-8 -*-


{
    "name": "Website Wildcard Domain",
    "summary": "Allows wildcard domain for linking same website to several sub-domains",
    "version": "14.0.2.0",
    'category': 'Website',
    'website' : "https://www.tosc.nl/",
    "author": "Deepa, " "The Open Source company (TOSC)",
    "description": """If a wildcard domain is set in the website, then it filters website by matching namespace,
        thus allowing to link several sub-domains associated to same Website..""",
    "depends": [
        "website",
    ],
    "data": [
        "views/website_views.xml",
    ],
}
