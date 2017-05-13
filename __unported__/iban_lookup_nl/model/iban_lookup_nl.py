# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Therp BV (<http://therp.nl>).
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
import logging
from openerp.osv import orm, fields
from openerp.addons.iban_lookup_nl.iban_lookup import iban_lookup
from openerp.addons.account_banking import sepa
from openerp.addons.account_banking_iban_lookup import online
from openerp.addons.account_banking.wizard.banktools import get_or_create_bank

logger = logging.getLogger('openerp.addons.iban_lookup_nl')


class iban_lookup_nl(orm.TransientModel):
    _name = 'iban.lookup.nl'

    def get_nl_partner_ids(self, cr, uid, context=None):
        partner_obj = self.pool.get('res.partner')
        if 'address' in partner_obj._columns:
            return self.get_nl_partner_ids_6(cr, uid, context=context)
        return partner_obj.search(
            cr, uid, ['|', ('country_id.code', '=', 'NL'), ('country_id', '=', False)],
            context=dict(context, active_test=False))

    def get_nl_partner_ids_6(self, cr, uid, context=None):

        def prio(address):
            if address.type in ('default', 'invoice', 'delivery') and address.street or address.city:
                return 6
            if address.street and address.city:
                return 5
            if address.street or address.city:
                return 3
            return 1

        address_obj = self.pool.get('res.partner.address')
        partner_ids = self.pool.get('res.partner').search(
            cr, uid, [], limit=0, context=dict(context, active_test=False))
        nl_partner_ids = []
        for partner_id in partner_ids:
            address_ids = address_obj.search(
                cr, uid, [('partner_id', '=', partner_id)],
                context=context)
            if not address_ids:
                nl_partner_ids.append(partner_id)
                continue
            addresses = address_obj.browse(
                cr, uid, address_ids, context=context)
            prio_nl = 0
            prio_other = 0
            for address in addresses:
                if not address.country_id:
                    continue
                if address.country_id.code == 'NL':
                    prio_nl = max(prio_nl, prio(address))
                else:
                    prio_other = max(prio_other, prio(address))
            if prio_nl >= prio_other:
                nl_partner_ids.append(partner_id)
        return nl_partner_ids

    def lookup_all(self, cr, uid, ids, context=None):
        partner_bank_obj = self.pool.get('res.partner.bank')
        bank_obj = self.pool.get('res.bank')

        bank_cache = {}
        def get_bank(bic):
            """
            Return browse object of bank by bic
            """
            if not bank_cache.get(bic):
                bank_id, _country = get_or_create_bank(
                    self.pool, cr, uid, bic)
                bank_cache[bic] = bank_obj.browse(
                    cr, uid, bank_id, context=context)
            return bank_cache[bic]

        def repr(iban):
            parts = []
            for i in range(0, len(iban), 4):
                parts.append(iban[i:i+4])
            return ' '.join(parts)

        # Get existing IBANs
        partner_ids = self.get_nl_partner_ids(cr, uid, context=context)
        partner_bank_ids = partner_bank_obj.search(
            cr, uid,
            [('state', '=', 'iban'),
             ('acc_number_domestic', '!=', False),
             ('acc_number_domestic', '!=', ''),
             '|', '&', ('country_id', '=', False),
                       ('partner_id', 'in', partner_ids),
                  ('country_id.code', '=', 'NL')], context=context)

        for account in partner_bank_obj.browse(
                cr, uid, partner_bank_ids, context=context):
            res = iban_lookup(account.acc_number_domestic)
            if not res:
                logger.warn(
                    'Error getting IBAN for %s (%s)', account.acc_number_domestic,
                    account.acc_number)
                continue
            logger.debug(
                'Lookup of %s (%s): %s (%s)', account.acc_number_domestic,
                account.acc_number, res.iban, res.bic)
            iban = repr(res.iban)
            if iban != account.acc_number:
                logger.info(
                    'Replacing IBAN %s by %s', account.acc_number, iban)
            
            bank = get_bank(res.bic)
            account.write({
                    'bank': bank.id,
                    'bank_name': bank.name,
                    'bank_bic': res.bic,
                    'acc_number': iban,
                    })

        # Now get regular accounts
        partner_bank_ids = partner_bank_obj.search(
            cr, uid,
            [('state', '=', 'bank'),
             '|', '&', ('country_id', '=', False),
                       ('partner_id', 'in', partner_ids),
                  ('country_id.code', '=', 'NL')], context=context)

        for account in partner_bank_obj.browse(
                cr, uid, partner_bank_ids, context=context):
            values = {}
            try:
                info = online.account_info('NL', account.acc_number)
                if info:
                    iban_acc = sepa.IBAN(info.iban)
                    if iban_acc.valid:
                        bank = get_bank(info.bic)
                        values = {
                            'acc_number_domestic': iban_acc.localized_BBAN,
                            'acc_number': unicode(iban_acc),
                            'state': 'iban',
                            'bank': bank.id,
                            'bank_bic': info.bic,
                            'bank_name': bank.name,
                            }
                        account.write(values)
                    else:
                        logger.warn(
                            'IBAN for %s not valid: %s',
                            account.acc_number, info.iban)
                else:
                    logger.warn(
                        'Error getting IBAN for %s', account.acc_number)
            except Exception, e:
                logger.warn(
                    'Error getting IBAN for %s: %s', account.acc_number, e)

        return {'type': 'ir.actions.act_window_close'}
