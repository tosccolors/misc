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
    "name": "Account Invoice Import Simple PDF from Email",
    "version": "12.0.0.0.0",
    "category": "Accounting/Accounting",
    "license": "AGPL-3",
    "summary": "Imports Pdf attachments as Invoice received from Vendor Email",
    "author": "Deepa, The Open Source Company (TOSC)",
    "depends": ["account_invoice_import_simple_pdf", "fetchmail", "account"],
    "excludes": ["account_invoice_import_invoice2data"],
    "website": "http://tosc.nl",
    # "external_dependencies": {"python": ["fitz", "regex", "dateparser"]},
    # fitz = pymupdf
    "data": [
        'data/res_config_settings.xml',
    ],
    "demo": [],
    "installable": True,
    "application": True,
}
