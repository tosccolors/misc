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
from openerp.addons.account_banking_iban_lookup.online import _account_info
from openerp.addons.account_banking.struct import struct
import xmlrpclib
logger = logging.getLogger('openerp.account_banking.iban_lookup_nl')

# Create a file config.py with the following contents:
#
# USER = '...'
# PASS = '...'
#

try:
    from openerp.addons.iban_lookup_nl.config import USER, PASS
except ImportError:
    logger.error('No authentication data found')
    USER = ''
    PASS = ''

def iban_lookup(account):
    proxy = xmlrpclib.ServerProxy('https://ibanconvert.therp.nl')
    iban, bic, error = proxy.iban_convert(
        USER, PASS, account)
    if error or not iban or not bic:
        logger.error('Error fetching IBAN for %s: %s', account, error)
        return False
    return struct(
        iban=iban.replace(' ', ''),
        account=account,
        bic=bic,
        bank=None,
        country_id=bic[4:6],
        code=bic[:6],
        )

# 1. Import mutable method with function pointers
# 2. Replace one of the pointers with local function
# 3. ???
# 4. Profit!
_account_info['NL'] = iban_lookup
