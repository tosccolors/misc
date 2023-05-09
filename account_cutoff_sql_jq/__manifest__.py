# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# © 2018 TOSC (Willem Hulshof <w.hulshof@tosc.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Cut-off SQL/jq',
    'version': '10.0.1.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'sql and/or job queue processing for all cutoff modules',
    'author': 'TOSC',
    'website': 'http://www.tosc.nl',
    'depends': [
    'account',
        'account_cutoff_base_operating_unit',
        'queue_job'
        ],
    'data': [
        'views/account_config_settings.xml',
        'views/account_cutoff.xml'
    ],
    'images': [
        ],
    'installable': True,
}
