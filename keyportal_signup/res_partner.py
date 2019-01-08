# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'



    @api.multi
    def _get_signup_url_for_action(self, action=None, view_type=None, menu_id=None, res_id=None, model=None):
        """ generate a signup url for the given partner ids and action, possibly overriding
            the url state components (menu_id, id, view_type) """
        res = super(ResPartner, self)._get_signup_url_for_action(
            self, action=action, view_type=view_type, menu_id=menu_id, res_id=res_id, model=model)

        for key, url in res.items():
            t1 = url.partition('/web/')
            t2 = t1[2].partition('?')
            res[key] = url + '#' + 'action=' + str(t2[0]) + '&' + str(t2[2])
        return res
    
