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
from osv import orm
from openerp import tools                                                      
from openerp.tools.translate import _                                          
from openerp.addons.mail.mail_message import decode

class mail_thread(orm.Model):
    """ 
    Take mail.thread company into account when searching for author of
    email (from) and partners (to, cc).
    """
    _inherit = 'mail.thread'

    def _get_force_company(
            self, cr, uid, context=None):
        '''Get company, if any, set on fetchmail server configuration.'''
        if context is None:
            return False
        # Find company for fetchmail configuration, if present
        fetchmail_server_id = (
            ('fetchmail_server_id' in context
             and context['fetchmail_server_id'])
            or False)
        if not fetchmail_server_id:
            return False
        fs_model = self.pool.get('fetchmail.server')
        fs_record = fs_model.read(
            cr, uid, fetchmail_server_id, ['company_id'], context=context)
        assert fs_record, (
            _('Fetchmail server record with id %d not found.') %
            fetchmail_server_id)
        return fs_record[['company_id'][0]  # might be False

    def _message_find_partners(
            self, cr, uid, message, header_fields=['From'], context=None):
        """ Find partners related to some header fields of the message.        
            1. Check wether this method exist on model to be created, in that
                case use model specific method.
            2. If there is no company on fetchmail server config, use the
                default method.
            3. Else find partner taking company into account."""   
        # Check for model specific method
        if 'model' in context and context['model']:
            fetchmail_model = self.pool.get(context['model'])
            assert fetchmail_model, (
                _('Model %s not found in pool') % context['model']) 
            # Model specific method no underscore prefix, as it is definitely
            # not private.
            if hasattr(fetchmail_model, 'message_find_partners'):
                return fetchmail_model.message_find_partners(
                    cr, uid, message, header_fields=header_fields,
                    context=context)
        # Check wether we should take company into account,
        # if not, call standard method:
        if (not 'force_company' in context
        or not context['force_company']):
            return super(mail_thread, self)._message_find_partners(
                        cr, uid, message, header_fields=header_fields,
                        context=context)
        # Find partners, taking company into account
        # Each email will return one or zero partners. Unless an
        # email address occurs in multiple headers.
        company_id = context['force_company']
        partner_obj = self.pool.get('res.partner')                             
        partner_ids = []                                                       
        s = ', '.join(
            [decode(message.get(h))
                for h in header_fields if message.get(h)])
        for email_address in tools.email_split(s):
            email_arg = ('email', 'ilike', email_address)
            company_arg = ('company_id', '=', company_id)
            no_company_arg = ('company_id', '=', False)
            user_arg = ('user_ids', '!=', False)
            # 1. Search user_partner within company:
            related_partners = partner_obj.search(
                cr, uid, [email_arg, user_arg, company_arg],
                limit=1, context=context)
            # 2. Search user_partner withouth company:
            if not related_partners:                                           
                related_partners = partner_obj.search(
                    cr, uid, [email_arg, user_arg, no_company_arg],
                    limit=1, context=context)
            # 3. Search partner within company:
            if not related_partners:                                           
                related_partners = partner_obj.search(
                    cr, uid, [email_arg, company_arg],
                    limit=1, context=context)
            # 4. Search partner withouth company:
            if not related_partners:                                           
                related_partners = partner_obj.search(
                    cr, uid, [email_arg, no_company_arg],
                    limit=1, context=context)
            partner_ids += related_partners                                    
        return partner_ids

    def message_process(
            self, cr, uid, model, message, custom_values=None,         
            save_original=False, strip_attachments=False,
            thread_id=None, context=None):
        context = context or {}
        local_context = dict(context)
        # Add force_company to context, if present in config
        force_company = (
            self._get_force_company(cr, uid, context=local_context))
        if force_company:
            local_context['force_company'] = force_company
        # Also put model in context, because we need it in overridden
        # methods that do not have it as an argument.
        local_context['model'] = model  # might be False
        # Now call original method
        return super(mail_thread, self).message_process(
            cr, uid, model, message, custom_values=custom_values,
            save_original=save_original, strip_attachments=strip_attachments,
            thread_id=thread_id, context=local_context)

