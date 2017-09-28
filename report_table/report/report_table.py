# -*- coding: utf-8 -*-
##############################################################################
#
#    UNamur - University of Namur, Belgium
#    Copyright (C) UNamur <http://www.unamur.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class ReportTable(models.AbstractModel):
    _name = 'report.report_table.report_json_table'

    @api.multi
    def render_html(self, docids, data=None):
        docids = docids or self._context.get('active_ids')
        if docids:
            docargs = {
                'docids': docids,
                'docs': self.env['report_table.json_table'].browse(docids)
            }
        elif data.get('tables'):
            json_tables = self.env['report_table.json_table']
            for table_dic in data['tables']:
                json_tables += json_tables.create_from_literal(**table_dic)
            docargs = {
                'docs': json_tables,
                'docids': docids,
            }
        docargs['eval'] = lambda x: safe_eval(x, {'res_company': self.env['res.company']._company_default_get()})
        return self.env['report'].render('report_table.report_json_table_template', docargs)
