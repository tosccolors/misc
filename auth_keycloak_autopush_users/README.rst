==================================================================
Keycloak: Auto-Push Users to Keycloak
==================================================================


When an user is created from Contacts, This module will then automatically push the user to Keycloak.
An email from Keycloak provider can also be triggered depending on flag set in the Providers.
In addition to it, can be configured whether the user receives an invitation mail from Odoo or not.

**Table of contents**

.. contents::
   :local:


Usage
=====


To use this module, you need to:

#. Go to Settings > Users & Companies > OAuth Providers
#. Set True for 'Email password reset link from Provider?' to trigger email from Keycloak.
#. Set True for 'Disable sending Welcome Mail from Odoo?' to prevent from sending welcome / invitation mail from Odoo.


Authors
~~~~~~~

* The Open Source Company (TOSC)


Contributors
~~~~~~~~~~~~

* Deepa Venkatesh <deepavenkatesh2015@gmail.com>

