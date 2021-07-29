.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=================
SQL Excel Reports
=================

The module allows users to fetch data from queries (stored as views) via a
Microsoft Excel add-in on their local Windows or Apple machine. The data is
loaded into a (hidden) worksheet, the report is visualized via a pivot table
and optionally a pivot chart. For each report the SQL view and layout of the
pivot table and chart are defined within Odoo.

Installation
============

* Install this module ``SQL Excel Reports`` in Odoo
* The module ``BI SQL Editor`` (menu item "SQL Views" under "Settings", "Database Stucture") will also be installed when not already present
* Install the Excel add-in on the user's Windows or Apple computer

The user configures the connection to Odoo via the ``Settings`` option,
from the Excel add-in Odoo menu on the Home tab of the ribbon.

Configuration
=============

* Create a SQL query with the ``BI SQL Editor`` (menu item ``SQL Views`` under Settings - Database Structure, enable ``Debug mode`` first) which generates a database view
* Create a report entry for an Excel report with module ``BI Excel Reports`` and refer to the database view
* Define the pivot table parameters: which fields are rows, columns, values and filters
* Define the pivot chart type, for example ``Clusterd Column``


Usage
=====

After activating the Excel add-in, the users will see three additional buttons on the Home ribbon:

* Get Report Index
* Get Reports
* Settings

The user must initially configure the connection to the Odoo server via
``Settings``. The ``Get Report Index`` option will fetch the list of available reports
onto a worksheet. Then the user makes a selection of reports.
Next, the ``Get Reports`` option will get the report data and format the pivot tables.

Technical info::

  The Excel add-in uses cURL (https://curl.se) to connect to Odoo. The Odoo jsonrpc request
  format is used. Received data is temporarily saved to disk before it is loaded into Excel.
  Add-in directories used on a Windows and Apple machine are respectively:

  Windows Excel add-in directory
  C:\Users\<username>\AppData\Roaming\Microsoft\AddIns

  Apple Excel add-in directory
  /Users/<username>/Library/Group Containers/UBF8T346G9.Office/User Content/Add-ins


Contributors
------------

* Vincent Verheul <v.verheul@magnus.nl>
* Site: https://magnus.nl
