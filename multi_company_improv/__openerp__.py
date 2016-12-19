# -*- coding: utf-8 -*-
##############################################################################
#
#    Multi-Company improvement module for OpenERP
#    Copyright (C) 2016 Magnus (http://www.magnus.nl). All Rights Reserved
#    @author Willem Hulshof <w.hulshof@magnus.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'multi_company_improv',
    'version': '1.0',
    'category': 'Generic Modules',
    'license': 'AGPL-3',
    'description': """
Multi Company Improvement
=========================

This module adds company_id to some models and adds multi-company rule to those models such,
that the user only sees the entries of his/her company


""",
    'author': "Magnus",
    'website': 'http://www.magnus.nl/',
    'depends': ['crm',
                'account_banking_sepa_credit_transfer',
                'account_banking'
    ],
    'data': [
        'security.xml',
        'crm_view.xml',
    ],
    'installable': True,
    'active': False,
}
