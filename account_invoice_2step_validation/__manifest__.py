# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2013 - 2018 Magnus - Willem Hulshof - www.magnus.nl
#
#
##############################################################################

{
    'name' : 'account_invoice_2step_validation',
    'version' : '0.9',
    'category': 'accounts',
    'description': """
This module adds authorization steps in workflow in supplier invoices.
=============================================================================

Enchanced to add
* Authorization
* Verification status on the Invoice

    """,
    'author'  : 'Magnus - Willem Hulshof',
    'website' : 'http://www.magnus.nl',
    'depends' : ['account',
		         'account_cancel',
		         'account_voucher',
                 "account_payment_order", # -- added: deep
                 "project",
                 'account_invoice_supplier_ref_unique',
                 'account_invoice_check_total',
                 'account_payment_partner'
    ],
    'data' : ["security/account_security.xml",
	          "views/res_company_view.xml",
              "views/res_partner_view.xml",
              "views/account_view.xml",
	          "views/account_invoice_view.xml",
              "wizard/wizard_view.xml",
              "security/ir.model.access.csv",
    ],
    'demo' : [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

