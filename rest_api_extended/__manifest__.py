# -*- coding: utf-8 -*-
# Copyright (C) 2024 The Open Source Company (<https://www.tosc.nl>)

{
    "name": "Rest API - Extended",
    "version": "16.0.2.0",
    "author": "Deepa Venkatesh (DK), The Open Source Company (TOSC)",
    "license": "AGPL-3",
    "website": "www.tosc.nl",
    "summary": "This app supports accepting of Analytic Ref & Country Code",
    "description": '''
Description
-----------
This app accepts Analytic Account Code/Ref sent as 'analytic_account_code', & then finds & updates with Analytic Account 'analytic_account_id'.
similarly for Country Code sent as 'country_code', will be replaced with 'country_id'
In Invoice, Analytic Distribution will be captured, when sent as 'analytic_distribution_code' in dict format
Ex: 'analytic_distribution_code': {'code001': 100}

To support backward compatibility, pass Single Analytic Account as 'single_analytic_code' which would be converted into Analytic Distribution with 100% cost allocation.
Ex: 'single_analytic_code': 'code001', would be captured into Analytic Distribution with 100%.

''',
    "category": "Other",
    "depends": [
        'rest_api',
    ],
    "data": [],
    "qweb":[],
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
