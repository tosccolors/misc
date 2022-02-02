# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2018 - 2022 Magnus Willem Hulshof
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": 'Accounting with Operating Units improvement',
    "summary": "Next to Introducing Operating Unit fields in invoices and "
               "Accounting Entries with clearing account, this module makes "
               "importing bank statements and payment orders per Operating Unit"
               "possible",
    "version": "10.0.1.1.0",
    "author": "Eficent, "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Magnus, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/operating-unit",
    "category": "Accounting & Finance",
    "depends": ['account','account_operating_unit'],
    "license": "LGPL-3",
    "data": [
        "views/account.xml",
        "views/account_move_view.xml",
    ],
    'installable': True,
}
