
# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2016 Magnus - Willem Hulshof - www.magnus.nl
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company like Veritos.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
##############################################################################
#
from openerp.osv import orm, fields


class crm_case_section(orm.Model):
    """ Model for sales teams. """
    _inherit = "crm.case.section"


    _columns = {
         'company_id': fields.many2one('res.company', 'Company', required=True),
    }

    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'crm.case.section', context=c),
    }

class banking_export_sepa(orm.Model):
    '''SEPA export'''
    _inherit = 'banking.export.sepa'

    _columns = {
         'company_id': fields.many2one('res.company', 'Company', required=True),
    }
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'banking.export.sepa', context=c),
    }