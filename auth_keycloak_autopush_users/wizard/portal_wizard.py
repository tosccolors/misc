# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo.tools import email_split

from odoo import api, fields, models, exceptions


def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''



class PortalWizardUser(models.TransientModel):

    _inherit = 'portal.wizard.user'


    def action_apply(self):
        res = super(PortalWizardUser, self).action_apply()
        usrIDS = []
        KCWiz = self.env['auth.keycloak.create.wiz']

        # Disable Signup token
        for wizard_user in self.sudo().with_context(active_test=False):
            if wizard_user.in_portal and wizard_user.user_id.id:
                wizard_user.partner_id.signup_cancel()
                if not wizard_user.user_id.oauth_uid:
                    usrIDS.append(wizard_user.user_id.id)

        if not usrIDS: return res

        # Push to Keycloak
        provider = self.env.ref(
            'auth_keycloak.default_keycloak_provider',
            raise_if_not_found=False
        )
        enabled = provider and provider.users_management_enabled
        if not enabled:
            raise exceptions.UserError(
                _('Keycloak provider not found or not configured properly.')
            )

        wiz = KCWiz.create({
            'provider_id': provider.id,
            'user_ids': [(6, 0, usrIDS)],
        })

        wiz.button_create_user()

        return res


    # Overridden:
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=False, signup_valid=False).create({
            'email': extract_email(self.email),
            'login': extract_email(self.email),
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
            'groups_id': [(6, 0, [])],
        })

    # Overridden:
    def _send_email(self):
        """ Disable sending signup mail from Odoo, if flagged"""

        provider = self.env.ref(
            'auth_keycloak.default_keycloak_provider',
            raise_if_not_found=False
        )
        disable = provider and provider.disable_welcome_email
        if disable:
            return True

        return super()._send_email()

