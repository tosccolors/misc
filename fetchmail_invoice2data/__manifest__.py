# -*- coding: utf-8 -*-
{
    'name': "Fetch Mail Invoice2data",

    'summary': """
            This Module establish relationship between mail.message and metadata attachment.
            It will also fill operation unit from server to attachment.
            Create Metadata attachment when attachment create.
    """,
    'description': """
    """,
        'author': "Magnus - DK",
        'website': "http://www.yourcompany.com",
        'category': 'Others',
        'version': '0.1',
        'depends': ['mail','attachment_base_synchronize','fetchmail','operating_unit'],
        'data': ['views/fetchmail_server_view.xml'],
        'demo': [],
    }