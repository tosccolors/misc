# -*- coding: utf-8 -*-


{
    'name': 'Fetchmail Tasks',
    'version': '12.0.0.0.0',
    'license': 'AGPL-3',
    'depends': [
        'fetchmail', 'project'
    ],
    'author': "The Open Source Company B.V.",
    'website' : "https://www.tosc.nl/",
    'category': 'Extra Tools',
    'sequence': 33,
    'description': """
This can be used to easily create email-based workflows for many email-enabled Odoo documents, such as:
----------------------------------------------------------------------------------------------------------
    * CRM Leads/Opportunities
    * CRM Claims
    * Project Issues
    * Project Tasks
    * Human Resource Recruitments (Applicants)
    
For Project Task:
----------------------------------------------------------------------------------------------------------
    Enhanced to map/link the Project based on Project code found in the Email Subject, 
    configure "Fetchmail: Link Project to Task" under Server Action in incoming servers.    

    """,

    'data': [
        'data/data.xml',
        'views/project_view.xml',
        'views/fetchmail_view.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
