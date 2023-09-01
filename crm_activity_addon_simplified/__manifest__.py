# -*- coding: utf-8 -*-
{
    'name': "crm_activity_addon_simplified",


    'summary': """
        This module simplifies the functionality of scheduling activities from the partner""",

    'description': """
        This module simplifies the functionality of scheduling activities from the partner form view and hides the fields "planned_revenue" and "probability" within the crm.lead object form view in order to keep activity management simple. 
        Also the action buttons "New Quotation", "Mark Won", "Mark Lost" in the crm.lead object will be hidden. This module hides the Pipeline menu as well. 
        This module adds a boolean field created_from_partner in crm.lead (activity) objects which will be set to true for crm.lead objects (activities) that have been created from the partner in order to be able to filter on those activities. 
        The "name" field within the crm.lead object will be auto-populated and read-only if the boolean created_from_partner is set to true. This module adds a pivot view to the Activities Log menu too.
    """,

    'author': "K.Sushma",
    'website': "http://www.tosc.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm_activity_addon','sale_advertising_order'],

    # always loaded
    'data': [
        'security/crm_security.xml',
        'report/crm_activity_report_views.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}