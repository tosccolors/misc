# -*- coding: utf-8 -*-


{
    "name": "Invoice Email Template Operating Unit",
    "summary": "Uses Email Template set in Operating Unit",
    "version": "10.0.3.1",
    'category': 'Tools',
    'website' : "https://www.tosc.nl/",
    "author": "Deepa, " "The Open Source company (TOSC)",
    "license": "LGPL-3",
    'description': """
Invoice Email Template Operating Unit
==========================================
This module uses the Template set in Operating Unit, for sending Email from Invoice.

Usage
-----

* Under Operating Unit, set template in the field 'Invoice Template'
* Module also has an ability to pick custom layout, provided a template exists with external_id in the below format

Tip
-----

To use a custom layout, you need to do the following ...

* Step 1: Export the record 'Invoice Notification Email',
* Step 2: Import back by making necessary changes, and set external_id as invoice_template_operating_unit.{OperatingUnit_CODE}
                
    """,
    "depends": [
          'operating_unit',
          "operating_unit_report_layout",
    ],
    "data": [
        "views/operating_unit_view.xml",
    ],
}

