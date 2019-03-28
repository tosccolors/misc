# -*- coding: utf-8 -*-
{
    'name' : 'Integrate Netherlands BTW Statement & Operating Unit',
    'version': '10.0.1.0.0',
    'category': 'Localization',
    'description': """
This module adds operating unit in Netherlands BTW Statement.
=============================================================================

    """,
    'author'  : 'Eurogroup Consulting - Willem Hulshof',
    'website' : 'http://www.eurogroupconsulting.nl',
    'depends' : ['l10n_nl_tax_statement','operating_unit',],
    'data' : ["views/l10n_nl_vat_statement_view.xml",
              "report/report_tax_statement.xml",
              "wizard/open_tax_balances_view.xml"],
    'demo' : [],
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: