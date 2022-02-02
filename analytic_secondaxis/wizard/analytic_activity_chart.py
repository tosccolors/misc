# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
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

from odoo import fields, models, api


class activities_analytic_chart(models.TransientModel):
    _name = 'activities.analytic.chart'
    _description = 'Analytic Activities Chart'

    from_date = fields.Date('From')
    to_date = fields.Date('To')

    @api.multi
    def analytic_activities_chart_open_window(self):
        mod_obj = self.env['ir.model.data']
        result_context = {}

        model, action_id = mod_obj.get_object_reference('analytic_secondaxis', 'action_activity_tree')
        [action] = self.env[model].browse(action_id).read()
        if self.from_date:
            result_context.update({'from_date': self.from_date})
        if self.to_date:
            result_context.update({'to_date': self.to_date})
        action['context'] = result_context
        return action
