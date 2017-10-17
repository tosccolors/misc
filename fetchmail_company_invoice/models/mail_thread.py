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
    def _get_force_company(self):
        '''Get company, if any, set on fetchmail server configuration.'''

        context = self._context

        if context is None:
            return False

        # Find company for fetchmail configuration, if present
        fetchmail_server_id = (
            ('fetchmail_server_id' in context
             and context['fetchmail_server_id'])
            or False)
        if not fetchmail_server_id:
            return False
        fs_model = self.env['fetchmail.server']

        CompanyID = False

        fs_record = fs_model.browse(fetchmail_server_id)
        assert fs_record, (
            _('Fetchmail server record with id %d not found.') %
            fetchmail_server_id)
        CompanyID = fs_record.company_id.id or False

        return CompanyID


    @api.multi
    def _find_partner_from_emails(self, emails, res_model=None, res_id=None, check_followers=True, force_create=False, exclude_aliases=True):
        """ Utility method to find partners from email addresses. The rules are :
            1 - check in document (model | self, id) followers
            2 - try to find a matching partner that is also an user (With Company)
                3 - try to find a matching partner that is also an user (Without Company)
            4 - try to find a matching partner (with Company)
                5 - try to find a matching partner (without Company)
            6 - create a new one if force_create = True

            :param list emails: list of email addresses
            :param string model: model to fetch related record; by default self
                is used.
            :param boolean check_followers: check in document followers
            :param boolean force_create: create a new partner if not found
            :param boolean exclude_aliases: do not try to find a partner that could match an alias. Normally aliases
                                            should not be used as partner emails but it could be the case due to some
                                            strange manipulation
        """
        if res_model is None:
            res_model = self._name
        if res_id is None and self.ids:
            res_id = self.ids[0]
        followers = self.env['res.partner']
        if res_model and res_id:
            record = self.env[res_model].browse(res_id)
            if hasattr(record, 'message_partner_ids'):
                followers = record.message_partner_ids

        Partner = self.env['res.partner'].sudo()
        Users = self.env['res.users'].sudo()
        partner_ids = []

        CompanyID = self._context.get('force_company', False)
        company_arg = ('company_id', '=', CompanyID)
        no_company_arg = ('company_id', '=', False)

        # Check wether we should take company into account,
        # if not, call standard method:
        if not CompanyID:
            return super(MailThread, self)._find_partner_from_emails(emails, res_model, res_id,
                                         check_followers, force_create, exclude_aliases)

        for contact in emails:
            partner_id = False
            email_address = tools.email_split(contact)
            if not email_address:
                partner_ids.append(partner_id)
                continue
            if exclude_aliases and self.env['mail.alias'].search([('alias_name', 'ilike', email_address)], limit=1):
                partner_ids.append(partner_id)
                continue

            email_address = email_address[0]
            # first try: check in document's followers
            partner_id = next((partner.id for partner in followers if partner.email == email_address), False)

            # second try: [2] - check in partners that are also users (with Company)
            # Escape special SQL characters in email_address to avoid invalid matches
            email_address = (email_address.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_'))
            email_brackets = "<%s>" % email_address
            if not partner_id:
                # exact, case-insensitive match
                partners = Users.search([('email', '=ilike', email_address), company_arg], limit=1).mapped('partner_id')
                if not partners:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    partners = Users.search([('email', 'ilike', email_brackets), company_arg], limit=1).mapped('partner_id')
                partner_id = partners.id

            # third try: [2] check in partners that are also users (without Company)
            if not partner_id:
                # exact, case-insensitive match
                partners = Users.search([('email', '=ilike', email_address), no_company_arg], limit=1).mapped('partner_id')
                if not partners:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    partners = Users.search([('email', 'ilike', email_brackets), no_company_arg], limit=1).mapped('partner_id')
                partner_id = partners.id

            # fourth try: [3] check in partners (with Company)
            if not partner_id:
                # exact, case-insensitive match
                partners = Partner.search([('email', '=ilike', email_address), company_arg], limit=1)
                if not partners:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    partners = Partner.search([('email', 'ilike', email_brackets), company_arg], limit=1)
                partner_id = partners.id

            # fifth try: [3] check in partners (without Company)
            if not partner_id:
                # exact, case-insensitive match
                partners = Partner.search([('email', '=ilike', email_address), no_company_arg], limit=1)
                if not partners:
                    # if no match with addr-spec, attempt substring match within name-addr pair
                    partners = Partner.search([('email', 'ilike', email_brackets), no_company_arg], limit=1)
                partner_id = partners.id

            if not partner_id and force_create:
                partner_id = self.env['res.partner'].name_create(contact)[0]
                if CompanyID:
                    Partner.browse(partner_id).write({'company_id': CompanyID})
            partner_ids.append(partner_id)
        return partner_ids




    @api.model
    def message_process(self, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None):

        local_context = self._context.copy()
        # Add force_company to context, if present in config
        force_company = (self.with_context(local_context)._get_force_company())

        if force_company:
            local_context['force_company'] = force_company
        # Also put model in context, because we need it in overridden
        # methods that do not have it as an argument.
        local_context['model'] = model  # might be False

        self = self.with_context(local_context)

        return super(MailThread, self).message_process(model, message, custom_values,
                        save_original, strip_attachments,
                        thread_id)
