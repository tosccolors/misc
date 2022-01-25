This directory contains files which are used by the wizard. The wizard presents these files to the user for downlaod:
- Odoo-reports.xlam
- OdooJsonToCsv
- OdooJsonToCsv.exe

Odoo-reports.xlam
This is the Microsoft Excel add-in which contains Visual Basic for Applications (VBA) code and a menu definition so the Odoo sub-menu appears in the Excel (Home) ribbon. Applicable for both Windows and Apple MacOS. See the wizard view for information on how to install is explained to the user.

OdooJsonToCsv
This is an optional helper program written in C (source code in OdooJsonToCsv.c) which is called by the Excel add-in to convert the Json file received from Odoo into a CSV file. The helper program is much faster compared to the same logic within the add-in (in VBA) and serves as an accelerator. The file OdooJsonToCsv (without extension) is the compiled version for Apple MacOS, OdooJsonToCsv.exe is the compiled version for Windows (64 bit).

OdooJsonToCsv on MacOS
Using the OdooJsonToCsv executable on MacOS requires setting the executable flag (with chmod +x) and configuration via the gatekeeper to allow execution, see https://disable-gatekeeper.github.io In addition, a Mac Script named OdooJsonToCsvScript.scpt must be created in directory ~/Library/Application Scripts/com.microsoft.Excel/  The script is created with the Script Editor which can be found in the Utilities apps.
Put this code into the script (which assumes that the OdooJsonToCsv executable is located in the Downloads directory):
on OdooJsonToCsvHandler(ParamString)
    do shell script "~/Downloads/OdooJsonToCsv " & ParamString
    return "Handler completed"
end OdooJsonToCsvHandler
