# -*- coding: utf-8 -*-

from openupgradelib import openupgrade



@openupgrade.migrate(use_env=True)
def migrate(env, version):

    if openupgrade.is_module_installed(env.cr, 'fetchmail_invoice'):
        openupgrade.update_module_names(
            env.cr,
            [('fetchmail_invoice', 'fetchmail_company_invoice')],
            merge_modules=True)
