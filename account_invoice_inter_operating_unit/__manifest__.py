# -*- coding: utf-8 -*-
# © 2013-2014 Odoo SA
# © 2015-2017 Chafique Delli <chafique.delli@akretion.com>
# © 2018 Willem Hulshof <w.hulshof@magnus.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Inter Company/Operating-Unit Module for Invoices',
    'summary': 'Intercompany Operating Unit invoice rules',
    'version': '10.0.1.1.0',
    'category': 'Accounting & Finance',
    'website': 'http://www.tosc.nl',
    'author': 'Odoo SA, Akretion, TOSC, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        # 'account_accountant', moved to enterprise
        'onchange_helper',
        'account_operating_unit',
        'account_invoice_2step_validation',
    ],
    'data': [
        'views/operating_unit_view.xml',
#        'views/res_config_view.xml',
    ],
    'demo': [
    ],
}
