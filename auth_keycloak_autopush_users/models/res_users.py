# -*- coding: utf-8 -*-


import logging


from odoo import api, fields, models, _


_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    def action_reset_password(self):
        """ Check Whether Mail needs to be sent from Odoo """

        provider = self.env.ref(
            'auth_keycloak.default_keycloak_provider',
            raise_if_not_found=False
        )
        disable = provider and provider.disable_welcome_email
        if disable:
            return True

        return super().action_reset_password()
