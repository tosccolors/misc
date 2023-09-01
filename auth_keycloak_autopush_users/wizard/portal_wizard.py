# -*- coding: utf-8 -*-

from odoo.tools.translate import _
from odoo.tools import email_split
from odoo.exceptions import UserError
from odoo.tools import email_normalize

from odoo import api, fields, models, exceptions
import logging

_logger = logging.getLogger(__name__)

def extract_email(email):
    """ extract the email address from a user-friendly email address """
    addresses = email_split(email)
    return addresses[0] if addresses else ''



class PortalWizardUser(models.TransientModel):

    _inherit = 'portal.wizard.user'

    # Overridden:
    def action_grant_access(self):
        """Grant the portal access to the partner.

        If the partner has no linked user, we will create a new one in the same company
        as the partner (or in the current company if not set).

        An invitation email will be sent to the partner, only if 'Disable Sending Welcome mail from Odoo' is set to False.
        Singup process will be skipped.
        """
        self.ensure_one()
        self._assert_user_email_uniqueness()

        if self.is_portal or self.is_internal:
            raise UserError(_('The partner "%s" already has the portal access.', self.partner_id.name))

        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')

        provider = self.env.ref(
            'auth_keycloak.default_keycloak_provider',
            raise_if_not_found=False
        )
        disableInviteMail = provider and provider.disable_welcome_email

        self._update_partner_email()
        user_sudo = self.user_id.sudo()

        if not user_sudo:
            # create a user if necessary and make sure it is in the portal group
            company = self.partner_id.company_id or self.env.company
            user_sudo = self.sudo().with_company(company.id).with_context(no_reset_password=disableInviteMail,
                                                                      signup_valid=False)._create_user()

        if not user_sudo.active or not self.is_portal:
            user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})

        # Check Whether Mail needs to be sent from Odoo
        if not disableInviteMail:
            self.with_context(active_test=True)._send_email()

        self._push_user2keycloak(user=user_sudo)

        return self.action_refresh_modal()

    def _push_user2keycloak(self, user):
        """ Automatically push user to Keycloak as soon as Portal User is created ."""

        KCWiz = self.env['auth.keycloak.create.wiz']
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
            'user_ids': [(6, 0, user.ids)],
        })

        wiz.button_create_user()

        return True

    #Overridden:
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users']._create_user_from_template({
            'email': email_normalize(self.email),
            'login': email_normalize(self.email),
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
            'groups_id': [(6, 0, [])],
        })
