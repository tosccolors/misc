# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models



class AuthOAuthProvider(models.Model):
    """Class defining the configuration values of an OAuth2 provider"""

    _inherit = 'auth.oauth.provider'
    _description = 'OAuth2 provider'
    _order = 'name'

    
    keycloak = fields.Boolean(string='Keycloak')
    