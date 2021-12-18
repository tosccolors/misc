This directory contains files which are used by the wizard. The wizard presents these files to the user for downlaod:
- Odoo-reports.xlam
- OdooJsonToCsvMac.exe
- OdooJsonToCsvWin.exe

Odoo-reports.xlam
This is the Microsoft Excel add-in which contains Visual Basic for Applications (VBA) code and a menu definition so the Odoo sub-menu appears in the Excel ribbon. Information on how to install is shown to the user: see the wizard view.

OdooJsonToCsv
This is optional, however it's mandatory when downloading data to CSV files instead of reports in Excel. It is a small helper program written in C (source code in OdooJsonToCsv.c) which is called by the Excel add-in to convert the Json file received from Odoo into a CSV file. The helper program is much faster compared to the same logic within the add-in (in VBA) and serves as an accelerator.


