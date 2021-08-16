.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

====================
BI SQL Excel Reports
====================

The module allows users to fetch data from queries (stored as views) via a
Microsoft Excel add-in on their local Windows or Apple machine. The data is
loaded into a (hidden) worksheet, the report is visualized via a pivot table
and optionally a pivot chart. For each report the SQL view and layout of the
pivot table and chart are defined within Odoo.

Installation
============

* Install this module ``BI SQL Excel Reports`` in Odoo
* The module ``BI SQL Editor`` (menu item "SQL Views" under "Settings", "Database Stucture") will also be installed when not already present
* The menu item for this module "SQL Excel Reports" will appear below the BI SQL Editor module
* Install the Excel add-in on the user's Windows or Apple computer

The user configures the connection to Odoo via the ``Settings`` option,
from the Excel add-in Odoo menu on the Home tab of the ribbon.

Configuration
=============

* Create a SQL query with the ``BI SQL Editor`` (menu item "SQL Views" under Settings - Database Structure, enable "Debug mode" first) which generates a database view
* Create a report entry for an Excel report with module ``BI SQL Excel Reports`` and refer to the database view
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

Example::

  Create a new query via "SQL Views", name it "Excel Module Odoo Overview" with techinal name
  "excel_module_odoo_overview". This will list all the available modules in Odoo with their
  installed status.

  Un-select "Is Materialized View" and enter the following for the query:

  SELECT
       md.id as x_module_id, md.name as x_module, md.shortdesc as x_shortdesc,
       md.author as x_author, md.website as x_website,
       md.state as x_state, md.license as x_license,
       mc.name as x_category, 1 as x_mod_count
  FROM
       ir_module_module as md
  LEFT JOIN ir_module_category as mc ON (mc.id = md.category_id)
  ORDER BY md.name

  Complete the steps via "Create SQL View, Indexes and Models" and "Create UI".
  Next, add an entry for an Excel report via "SQL Excel Reports", enter a unique code for the
  report and give it a name, for example "Demo - Odoo Modules". Enter the technical name of the
  query we just created: excel_module_odoo_overview. Enter "Stacked Bar" for the Chart Type and
  enter "Modules" for the short name (whis will be the name of the worksheet in Excel).

  Complete the Excel report layout definition by adding fields for the pivot table:
  - field x_author as filter
  - field x_state for columns
  - field x_category for rows
  - field x_module for rows and unselect "details"
  - field x_mod_count for values
  - field x_category as a slicer with slicer-top 8 and slicer-height 304
  - field x_state as a slicer with slicer-top 317 and slicer-height 93
  Optionally add alias descriptions for the fields.

  After you have installed the Excel Add-in, you should see an "Odoo" section in the
  "Home" ribbon in Excel. Click Settings and complete the form so Excel knows how to connect
  to Odoo. Use the Test button to check and click OK to save your settings. Next, click the
  "Get Index" option which will fetch a list of available reports from Odoo. Select the report
  by putting an "x" in column B to replace the "." and click the "Get Reports" option. Excel
  will now fetch the data from Odoo and format a pivot table & chart on worksheet "Modules".
  The data is available in a hidden worksheet "Modules data"

Contributors
------------

* Vincent Verheul <v.verheul@magnus.nl>
* Site: https://magnus.nl
