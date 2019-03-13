# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Batch Vendor Invoice Import New',
    'version': '10.0.1.0.0',
    'author': 'Willem Hulshof',
    'maintainer': 'Willem Hulshof',
    'website': 'www.magnus.nl',
    'license': '',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml # noqa
    # for the full list
    'category': 'imports',    'summary': 'Automatic import of vendor invoices ',
    'description': """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
batch_vendor_invoice_import_new
===============================

This module extends the functionality of account_invoice_import to support batch importing of vendor invoices
and to allow you to not having to use the single invoice upload in the mentioned module. 
This possibility remains for testing purposes. This is the version that makes no use of import-export and a separate
OCR-process

Installation
============

To install this module, you need to:

#. define file_location in external_file_location module

Configuration
=============

To configure this module, you need to:

#. Go to ...

.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

Usage
=====

To use this module, you need to:

#. Go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

* Add ...

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

* Firstname Lastname <email.address@example.org>
* Second Person <second.person@example.org>

Funders
-------

The development of this module has been financially supported by:

* Company 1 name
* Company 2 name

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
* If you have any questions, please contact Savoir-faire Linux
(support@savoirfairelinux.com)
""",

    # any module necessary for this one to work correctly
    'depends': ['external_file_location',
                'account_operating_unit',
                'account_invoice_import_invoice2data'
    ],
    'external_dependencies': {
        'python': [],
    },

    # always loaded
    'data': [
            'data/external_file_location.xml',
            'views/account_invoice_import_config_view.xml',
            'views/task_view.xml',
            'views/attachment_view.xml',
            'views/res_partner_view.xml',
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
    'application': True,
}
