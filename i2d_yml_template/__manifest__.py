# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'YML template module',
    'version': '10.0.1.0.0',
    'author': 'Willem Hulshof, D. Prosee',
    'maintainer': 'Willem Hulshof',
    'website': 'www.magnus.nl',
    'license': '',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml # noqa
    # for the full list
    'category': 'Configuration',    'summary': 'Template manager for invoice2data',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
i2d_yml_template
================

This module extends the functionality of OCA edi/account_invoice_import_invoice2data to support maintaining templates.

Installation
============

To install this module, you need to:

* Nothing special

Configuration
=============

To configure this module, you need to:

* provide a key in odoo config to indicate the template directory e.g. invoice2data_templates_dir=/odoo/i2d_yml_templates
* configure the external locations given in the data directory of this module with proper file directories



Usage
=====

To use this module, you need to:

* Go to accounting/...../yml templates
* Give template a name
* Load an example PDF; this will trigger text parsing. The result will be shown.
* Use the output of the parsed pdf to create the regex expressions
* Implement the regex expressions in the yml template
* Don't forget to connect to an existing partner, identified with its vat number
* Save and export yml template
* Possibly test the template using this module or accounting/.../import vendor bills
* Enjoy

Known issues / Roadmap
======================

* The regexr.com iframe could be filled by the parsed text using the query text=html.escape(self.parsed_pdf)
  This requires javascript to update the src attribute of the iframe
  The text should, of course, be html encoded to be shipped via the query

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* W\. Hulshof
* D\. Prosee

Funders
-------

The development of this module has been financially supported by:

* BDU Holding
* New Skool Media

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.


* Module exported by the Module Prototyper module for version 10.0.
* If you have any questions, please contact Savoir-faire Linux (support@savoirfairelinux.com)

""",

    # any module necessary for this one to work correctly
    'depends': ['batch_vendor_invoice_import',
    ],
    'external_dependencies': {
        'python': [],
    },

    # always loaded
    'data': ['security/ir.model.access.csv',
             # 'data/external_file_location.xml',
             'views/i2d_yml_template_view.xml',
             'views/attachment_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

    'js': [],
    'css': [],
    'qweb': [],

    'installable': True,
    # Install this module automatically if all dependency have been previously
    # and independently installed.  Used for synergetic or glue modules.
    'auto_install': False,
    'application': False,
}
