# -*- coding: utf-8 -*-
{
    'name': "Fetch Mail Invoice2data",

    'summary': """

            This modules is used to create vendor invoices via e-mail. It depends on two other modules:
            
            - batch vendor import invoice new
            - yml template module
            
            
    """,
    'description': """
    """,
        'author': "TOSC - DK",
        'website': "http://www.tosc.nl",
        'category': 'Others',
        'version': '0.1',
        'depends': ['mail',
        # 'attachment_queue',
        'attachment_queue',
        'fetchmail','operating_unit',
        # 'fetchmail_attach_from_folder'
        ],
        'data': [
        # 'views/fetchmail_server_view.xml',
         'views/attachment_view.xml'],
        'demo': [],
    }