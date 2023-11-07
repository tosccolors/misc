==================================================================
Keycloak: Auto-Push Users to Keycloak & Disable Odoo Password
==================================================================


This module will automatically push the Portal user to Keycloak, which inturn will send password mails to user from Keycloak.
Also disables password changing in Odoo & login, such that User has to login via Keycloak Auth provider,
optionally it can be configured whether to send invitation mail from Odoo or not.
Note: this would disable password re-setting.

**Table of contents**

.. contents::
   :local:


Usage
=====


To use this module, you need to:

#. Go to Settings > Users & Companies > OAuth Providers
#. Set True for 'Email password reset link?'

Note: Remove Access Groups from Technical Settings for 'Change Password' (base.change_password_wizard_action)