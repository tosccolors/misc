# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'YML template module',
    'version': '10.0.1.0.0',
    'author': 'Willem Hulshof',
    'maintainer': 'Willem Hulshof',
    'website': 'www.tosc.nl',
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

#. Nothing special

Configuration
=============

To configure this module, you need to:
# Configure the folder structure on a location accessible by the finance department, where *.pdf and *.PDF invoice documents are placed before import and moved after successful import, like "invoices_in" and "invoices_done". 
# Configure an FTP connection with which Odoo can access one or more folders to retrieve supplier invoice documents. 
# Create the YML template file export location "invoice2data_local_templates" under data/ or .filestore/ (depends on production or test database) to get the path "home/odoo/data/invoice2data_local_templates".
# Include this directory in the "odoo.cfg"-file and restart the server. 
## invoice2data_templates_dir = /opt/invoice2data_local_templates. 
## invoice2data_exclude_built_in_templates = True). 
# Install the following modules: 
## i2d_yml_template_new (should install the following modules). 
## batch_vendor_invoice_import_new. 
## account_invoice_import_invoice2data. 
## external_file_location. 
## account_operating_unit. 
# Configure in Settings > Automation > File locations the following: 
## Import vendor invoices: 
### Protocol = FTP. 
### Port = 21 (often). 
### Task configuration (for each file type in each folder a separate task is required, so per operating unit folder 2 tasks): 
#### Method Type = "Import". 
#### Filename = *.pdf or *.PDF. 
#### Filepath = [name of specific folder accessible by Odoo via FTP to retrieve the document]. 
#### Location = "Import Vendor Invoices". 
#### Operating Unit which is needed. 
#### After import = "Move". 
#### Move path = [name of specific folder accessible by Odoo via FTP to move the document]. 
## Default export location for i2d yml templates: 
### Protocol = File Store. 
### File Store Root Path = write exactly "data/", or that what has been configured in the filesystem for storing YML templates. 
### Task configuration (1 task): 
#### Method Type = "Export". 
#### Filepath = "invoice2data_local_templates". 
#### Location = "Default export location for i2d yml templates". 
#### Operating Unit can be left empty. 
# Configure a default supplier by creating a new (empty) partner with the boolean "default supplier" = True in the tab "Sales". 
# Configure the scheduled actions "Run file exchange tasks" and "Run Attachments Metadata": 
## Set to Active = True. 
## Set the interval (in minutes). 
## Make sure the res.user in the tasks has an e-mail address filled.
# Go to Finance > Configuration > Import Vendor Bills > Import Bills and create an import configuration for the Default (Dummy) Supplier. 
## Set the partner to the created Default Supplier. 
## Set the Method for Invoice Line to "Single Line, No Product"
## Set the Expense Account to anything you like.
# Go to Finance > Configuration > YML Templates to configure company-specific invoice import templates using regex. 
## Fill all required fields such as Name, Template Vendors (here you add the Vendor name, VAT number, 'Import Vendor Bill') and the YML content. 
## The YML content consists of regular expressions, which need to match with the text as parsed by Odoo (see the database log to extract the correct parsed text).

Usage
=====

To use this module, you need to:

#. Go to accounting/.....

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
* If you have any questions, please contact Savoir-faire Linux
(support@savoirfairelinux.com)
""",

    # any module necessary for this one to work correctly
    'depends': ['batch_vendor_invoice_import_new',
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
