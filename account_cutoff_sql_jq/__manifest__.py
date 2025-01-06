# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2022 Magnus (<http://www.magnus.nl>). All Rights Reserved
#    Copyright (C) 2022-2024 TOSC (<http://www.tosc.nl>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Cut-off SQL/jq',
    'version': '16.0.2.0.0',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'sql and/or job queue processing for all cutoff modules',
    'author': 'Magnus, Deepa Venkatesh (DK), The Open Source Company (TOSC)',
    'website': 'http://www.tosc.nl',
    'depends': [
        'account_cutoff_base',
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
