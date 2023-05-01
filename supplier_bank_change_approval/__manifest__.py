# -*- coding: utf-8 -*-
{
    'name': "Supplier Bank Account Approval",

    'summary': """
        Supplier Bank Account Approval""",

    'description': """
        \n1.Add state draft and confirmed to the banks_account_ids from partner.
        \nThis should only apply to partners is supplier = true
        \n2.New menu called 'Sensitive fields approval' where any changes can be approved. 
        \nThis menu should only be visible and available to new security group 'Bank Account Manager'
        \n3.When a bank account is changed or added, it will be in draft state. It cannot be used in any invoice or payment.
        \nwhen creating an invoice or payment which says that "The supplier has changed bank details which are not yet approved.
        """,

    'author': "Magnus-Sify",
    'website': "http://www.magnus.nl",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_payment_order'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'demo/demo.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}