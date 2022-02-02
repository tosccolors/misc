# -*- coding: utf-8 -*-
{
    'name': "deactivate_crm_lead_dashboard_count",

    'summary': """
        This module deactivates counting crm.lead records in the smart buttons available on the sales dashboard, in order to not reduce the performance in case of many crm.lead records.
    """,

    'description': """This module deactivates counting crm.lead records in the smart buttons available on the sales dashboard, in order to not reduce the performance in case of many crm.lead records.
        
    """,

    'author': "Magnus - DK",
    'website': "http://www.yourcompany.com",

    'category': 'Others',
    'version': '0.1',
    'depends': ['sale','crm','sale_advertising_order','sales_team'],

    'data': [
#        'views/sales_team_dashboard.xml',
    ],
    'qweb': [
        "static/src/xml/sales_team_dashboard.xml",
    ]
    
}
