==================================================================
Keycloak: Disable Odoo Password & Auto-Push Users to Keycloak
==================================================================


This module disable password changing in Odoo & login, such that User has to login via Keycloak Auth provider,
Auto-pushes the Portal user to Keycloak, which inturn will send password mails to user from Keycloak.
Note: this would disable both password setting & invitation mail from Odoo.

**Table of contents**

.. contents::
   :local:


Usage
=====


To use this module, you need to:

#. Go to Settings > Users & Companies > OAuth Providers
#. Set True for 'Email password reset link?'

Note: Remove Access Groups from Technical Settings for 'Change Password' (base.change_password_wizard_action)