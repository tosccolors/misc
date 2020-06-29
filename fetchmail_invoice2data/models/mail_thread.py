# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    This module copyright (c) 2013 Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tools.mail import decode_smtp_header
from odoo import _, api, fields, models
from odoo import tools

import email
import xmlrpclib

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _get_metadata_creation_rule(self):
        '''Get metadata creation rule, if any, set on fetchmail server configuration.'''

        context = self._context

        if context is None:
            return False

        # Find metadata creation rule for fetchmail configuration, if present
        fetchmail_server_id = (
                ('fetchmail_server_id' in context
                 and context['fetchmail_server_id'])
                or False)
        if not fetchmail_server_id:
            return False
        fs_model = self.env['fetchmail.server']

        fs_record = fs_model.browse(fetchmail_server_id)
        assert fs_record, (
                _('Fetchmail server record with id %d not found.') %
                fetchmail_server_id)
        metadata_creation_rule = fs_record.metadata_attachment or False
        return metadata_creation_rule

    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):

        local_context = self._context.copy()
        # Add force_company to context, if present in config
        OperationUnit = (self.with_context(local_context)._get_operating_unit())

        if OperationUnit:
            local_context['operating_unit_id'] = OperationUnit
        # Also put model in context, because we need it in overridden
        # methods that do not have it as an argument.
        local_context['model'] = model  # might be False

        self = self.with_context(local_context)

        res =  super(MailThread, self).message_process(model, message, custom_values,
                        save_original, strip_attachments,
                        thread_id)
        
        return res
    