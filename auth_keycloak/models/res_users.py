# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug.urls
import urlparse
import urllib2
import json

from odoo import api, fields, models
from odoo.exceptions import AccessDenied
from odoo.addons.auth_signup.models.res_users import SignupError

from odoo.addons import base
base.res.res_users.USER_PRIVATE_FIELDS.append('oauth_access_token')

class ResUsers(models.Model):
    _inherit = 'res.users'


    @api.model
    def _auth_oauth_rpc(self, endpoint, access_token, provider):
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        if oauth_provider.keycloak:
            params = werkzeug.url_encode({'Authorization': 'bearer ' + access_token})
            if urlparse.urlparse(endpoint)[4]:
                url = endpoint + '&' + params
            else:
                url = endpoint + '?' + params
        else:
            params = werkzeug.url_encode({'access_token': access_token})
            if urlparse.urlparse(endpoint)[4]:
                url = endpoint + '&' + params
            else:
                url = endpoint + '?' + params
        f = urllib2.urlopen(url)
        response = f.read()
        return json.loads(response)

    @api.model
    def _auth_oauth_validate(self, provider, access_token):
        """ return the validation data corresponding to the access token """
        oauth_provider = self.env['auth.oauth.provider'].browse(provider)
        validation = self._auth_oauth_rpc(oauth_provider.validation_endpoint, access_token, provider)
        if validation.get("error"):
            raise Exception(validation['error'])
        if oauth_provider.data_endpoint:
            data = self._auth_oauth_rpc(oauth_provider.data_endpoint, access_token, provider)
            validation.update(data)
        return validation

