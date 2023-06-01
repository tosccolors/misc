======================
Pdf Background Image
======================


This module was written to add backgrounds image to PDF reports. Because of the way wkhtmltopdf handles headers and footers in the current versions, it is quite impossible to have a background for the complete page using HTML and CSS. That is why this module inserts the image at the PDF level.

**Table of contents**

.. contents::
   :local:

Installation
============


As PyPDF is not supported in python3, you need to install PyPDF2::

$ pip install pypdf2

Usage
=====

To use this module, you need to:

#. go to your company
#. select a PDF or image to use as background. Note that resolutions and size must match.
