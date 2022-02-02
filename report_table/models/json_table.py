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

from odoo import models, fields
import json


class JSONTable(models.TransientModel):
    _name = 'report_table.json_table'

    name = fields.Char("Name", help="Short name, will be used as worksheet title if exported to XLSX", required=True)
    title = fields.Html("Title", help="Title part of the table, used as header of the report")
    header = fields.Text("Header", help="Header row of the table, in JSON format")
    rows = fields.Text("Rows", help="Rows of the table, in JSON format")
    css_class = fields.Char("CSS Class", help="CSS class on the table")
    css = fields.Text("CSS", help="CSS to add to the report")

    def create_from_literal(self, name, title=None, header=None, rows=None, css_class=None, css=None):
        vals = {
            "name": name,
            "title": title or False,
            "header": json.dumps(header or False),
            "rows": json.dumps(rows or False),
            "css_class": css_class,
            "css": css
        }
        return self.create(vals)

    def to_literal(self):
        return {
            "name": self.name,
            "title": self.title,
            "header": json.loads(self.header or "false"),
            "rows": json.loads(self.rows or "false"),
            "css_class": self.css_class,
            "css": self.css
        }

    def to_literals(self):
        return self.mapped(lambda t: t.to_literal())
