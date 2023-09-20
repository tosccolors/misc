# -*- coding: utf-8 -*-

import string
import re
from odoo import api, models, _
from odoo.tools.misc import ustr

class Partner(models.Model):
    _inherit = 'res.partner'


    # Netherlands VAT verification
    __check_vat_nl_re = re.compile("(?:NL)?[0-9]{9}B[0-9]{2}") #check for character B
    # __check_vat_nl_re = re.compile("(?:NL)?[0-9A-Z+*]{10}[0-9]{2}")


    def check_vat_nl(self, vat):
        """
        Temporary Netherlands VAT validation to support the new format introduced in January 2020,
        until upstream is fixed.
        Algorithm detail: http://kleineondernemer.nl/index.php/nieuw-btw-identificatienummer-vanaf-1-januari-2020-voor-eenmanszaken
        TODO: remove when fixed upstream
        """
    
        try:
            from stdnum.util import clean
            from stdnum.nl.bsn import checksum
        except ImportError:
            return True

        vat = 'NL'+vat #append NL for lenth 14
        vat = clean(vat, ' -.').upper().strip()

        if not (len(vat) == 14):
            return False
    
        # Check the format
        match = self.__check_vat_nl_re.match(vat)
        if not match:
            return False
    
        # Match letters to integers
        char_to_int = {k: str(ord(k) - 55) for k in string.ascii_uppercase}
        char_to_int['+'] = '36'
        char_to_int['*'] = '37'
    
        # Remove the prefix
        vat = vat[2:]
    
        # 2 possible checks:
        # - For natural persons
        # - For non-natural persons and combinations of natural persons (company)
    
        # Natural person => mod97 full checksum
        check_val_natural = '2321'
        for x in vat:
            check_val_natural += x if x.isdigit() else char_to_int[x]
        if int(check_val_natural) % 97 == 1:
            return True
    
        # Company => weighted(9->2) mod11 on bsn
        vat = vat[:-3]
        if vat.isdigit() and checksum(vat) == 0:
            return True
    
        return False