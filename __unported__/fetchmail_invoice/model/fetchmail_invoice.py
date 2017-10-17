# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2012 Therp BV (<http://therp.nl>).
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

from odoo import tools, api, fields, models, _
from odoo.tools.translate import _
from odoo.tools.mail import decode_smtp_header
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = 'account.invoice'

    @api.cr_uid_context
    def get_partner_from_mail(
            self, cr, uid, email_address, company_id, force_supplier=False,
            context=None):
        partner_model = self.pool.get('res.partner')                             
        email_arg = ('email', 'ilike', email_address)
        company_arg = ('company_id', '=', company_id)
        no_company_arg = ('company_id', '=', False)
        user_arg = ('user_ids', '!=', False)
        supplier_arg = ('supplier', '=', True)
        # Build search criteria array.
        args_list = []

        if force_supplier:
            # Searching just for suppliers, we do not care about user
            if company_id:
                args_list.append([email_arg, supplier_arg, company_arg])
                args_list.append([email_arg, supplier_arg, no_company_arg])
            else:
                args_list.append([email_arg, supplier_arg])
        else:
            # First search user, then supplier, then any partner.
            if company_id:
                args_list.append([email_arg, user_arg, company_arg])
                args_list.append([email_arg, user_arg, no_company_arg])
                args_list.append([email_arg, supplier_arg, company_arg])
                args_list.append([email_arg, supplier_arg, no_company_arg])
                args_list.append([email_arg, company_arg])
                args_list.append([email_arg, no_company_arg])
            else:
                args_list.append([email_arg, user_arg])
                args_list.append([email_arg, supplier_arg])
                args_list.append([email_arg])
        for args in args_list:
            related_partners = partner_model.search(
                cr, uid, args, limit=1, context=context)
            if related_partners:
                return related_partners
        return []

    @api.cr_uid_context
    def message_find_partners(
            self, cr, uid, message, header_fields=['From'], context=None):
        """ Find partner for supplier invoice. Problem is that either the
        sender (from), or the receiver (to, cc) must be a supplier, but this
        method is called first to determine the sender/author_id, and only
        later for the receiver (partner_ids). To handle this we will also
        search - as a fallback - partners that are not suppliers. Only later
        we need to check that either the sender, or the receiver is a
        supplier.
        NOT a private method (no _ prefix), because called from mail_thread.
        """   
        # Find partners, taking company into account, and having a preference
        # for suppliers.
        # Each email will return one or zero partners. Unless an
        # email address occurs in multiple headers.

        company_id = (
            ('force_company' in context
             and context['force_company']) or False)
        partner_ids = []                                                       
        s = ', '.join(
            [decode_smtp_header(message.get(h))
                for h in header_fields if message.get(h)])
        for email_address in tools.email_split(s):
            partner_ids += self.get_partner_from_mail(
                cr, uid, email_address, company_id, context=context)
        return partner_ids

    @api.cr_uid_context
    def _is_partner_supplier(self, cr, uid, partner_id, context=None):
        assert partner_id, _(
            'This method should be called with a valid partner id')
        partner_model = self.pool.get('res.partner')
        partner_record = partner_model.read(
            cr, uid, partner_id, ['supplier'], context=context)
        assert partner_record, _('No partner found for id %d') % (partner_id,)
        return partner_record['supplier']

    @api.cr_uid_context
    def message_new(
        self, cr, uid, msg_dict, custom_values=None, context=None):
        """
        Override this mail.thread method in order to compose a set of
        valid values for the invoice to be created
        """       
        if context is None:
            context = {}
        # prevent changes in context from "bubbling up" to calling methods
        local_context = dict(context)

        users_pool = self.pool.get('res.users')
        base_model = self.pool.get('ir.model.data')
        partner_model = self.pool.get('res.partner')                             

        # As the scheduler is run without language,
        # set the administrator's language
        if not local_context.get('lang'):
            user = users_pool.browse(cr, uid, uid, context=local_context)
            local_context['lang'] = user.partner_id.lang

        if custom_values is None:
            custom_values = {}
        email_from = msg_dict.get('from', False)
        if email_from:
            custom_values['name'] = _("Received by email from %s") % email_from
        email_date = msg_dict.get('date', False)
        if email_date:
            custom_values['date_invoice'] = email_date

        company_id = (
            ('force_company' in local_context
             and local_context['force_company']) or False)

        # Retrieve partner_id from message dictionary.
        # Partner might be:
        # 1. Supplier sending email (author_id in msg dict.)
        # 2. Partner receiving message (special partner setup to receive
        #    email). Should be linked to the appropiate company in multi-
        #    company databases.
        # 3. Dummy invoice partner.
        # Partner MUST be a supplier.

        # 1. Try author:
        supplier_partner_id = False
        author_id = (
            'author_id' in msg_dict and msg_dict['author_id'] or False)
        if (author_id
        and self._is_partner_supplier(
                cr, uid, author_id, context=local_context)):
            supplier_partner_id = author_id

        # 2. Try recipients:
        # Unfortunately we have to do a new lookup on partner, because
        # the method message_process in mail_thread removes the partner_ids
        # already found, from the message dictionary:
        if not supplier_partner_id:
            s = ', '.join(
                [msg_dict.get(h)
                    for h in ['to', 'cc'] if msg_dict.get(h)])
            for email_address in tools.email_split(s):
                partner_ids = self.get_partner_from_mail(
                    cr, uid, email_address, company_id, force_supplier=True,
                    context=local_context)
                if partner_ids:
                    supplier_partner_id = partner_ids[0]
                    break

        # 3. Try default partner for company (company might be False):
        if not supplier_partner_id:
            args = [('fetchmail_invoice_default', '=', True),]
            if company_id:
                    args.append(('company_id', '=', company_id))
            default_ids = partner_model.search(
                cr, uid, args, context=local_context)
            if default_ids:  # can be only one
                supplier_partner_id = default_ids[0]

        # We should have a supplier/partner by now....
        assert supplier_partner_id, _('No partner found to link invoice to')

        # Get company for supplier, if any. If present, should be the same
        # as company for fetchmail config, if present. If still no
        # company is found, use main company.
        supplier_record = partner_model.read(
            cr, uid, supplier_partner_id, ['company_id', 'supplier'],
            context=local_context)
        supplier_company_id = (
            supplier_record['company_id'] and supplier_record['company_id'][0]
            or False)
        if supplier_company_id:
            if company_id:
                assert company_id == supplier_company_id, (_(
                    'Supplier found not valid for company %d.') %
                    company_id)
            else:
                company_id = supplier_company_id
        if not company_id:
            # Last resort, use main company
            company_id = base_model.get_object_reference(                                
                    cr, uid, 'base', 'main_company')[1]
        
        # Now we should have a company, and we should use it for everything
        assert company_id, (_(
            'All attempts to determine company for invoice failed'))
        local_context['force_company'] = company_id
        
        # Paranoid check
        assert supplier_record['supplier'], (_(
            'Partner %d is not a supplier') % supplier_partner_id)

        # And we should have an account property
        # (read again, as company might have changed)
        supplier_record = partner_model.read(
            cr, uid, supplier_partner_id, ['property_account_payable_id'],
            context=local_context)
        assert supplier_record['property_account_payable_id'], (
            _('No account payable on partner %d.') % supplier_partner_id)

        # And we need some information in context as well
        local_context.update({
            'company_id': company_id,
            'type': 'in_invoice',
        })

        supplier = partner_model.browse(cr, uid, supplier_partner_id, context=local_context)

        journal_id = self.pool.get('account.invoice').default_get(cr, uid, ['journal_id'], context=local_context)['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sale journal for this company.'))

        custom_values.update({
            'company_id': company_id,
            'partner_id': supplier_partner_id,
            'type': 'in_invoice',

            'account_id': supplier.property_account_payable_id.id,
            'journal_id': journal_id,
        })


        # custom_values.update(
        #     self.onchange_partner_id(
        #         cr, uid, [], 'in_invoice', supplier_partner_id,
        #         company_id=company_id)['value'])

        # Create the resource
        res_id = super(account_invoice, self).message_new(
            cr, uid, msg_dict, custom_values=custom_values,
            context=local_context)
        return res_id

