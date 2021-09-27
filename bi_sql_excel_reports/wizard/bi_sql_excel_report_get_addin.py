# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from odoo import api, fields, models


class GetAddInFile(models.TransientModel):
    _name = 'bi.sql.excel.addinfile.wizard'

    excel_add_in_name = 'Odoo-reports.xlam'

    file_name = fields.Char(
        string='File name',
        readonly=True)
    addin_data = fields.Binary(
        string='File data',
        readonly=True,
        help='Download Excel Add-in for SQL Excel Reports')
    has_data = fields.Boolean(
        string='Data loaded',
        default=False,
        help='Indicates that the Excel Add-in has been loaded')

    def _get_addin_binary(self):
        """ Get the Excel Add-in file from the source directory """
        delim = '/' if '/' in __file__ else '\\'
        file_parts = __file__.split(delim)[:-2]
        file_parts.append('excel_add_in')
        file_parts.append(self.excel_add_in_name)
        file_path = delim.join(file_parts)
        with open(file_path, 'rb') as f:
            addin_data = f.read()
        return addin_data

    def _add_log_entry(self, message, line=0):
        """ Add to the log table (ir.logging) which user interface is in Settings - Database Structure - Logging """
        level = 'info'
        func = 'Download ' + self.excel_add_in_name + ' by ' + self.env.user.name
        path = 'action'
        record_type = 'server'
        with self.pool.cursor() as cr:
            cr.execute("""
                INSERT INTO ir_logging(create_date, create_uid, type, dbname, name, level, message, path, line, func)
                VALUES (NOW() at time zone 'UTC', %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.env.uid, record_type, self._cr.dbname, __name__, level, message, path, line, func))

    @api.multi
    def prepare_addin_file(self):
        """ Prepare the Excel Add-in for download and (re-) open the form with data loaded """
        addin_data = self._get_addin_binary()
        self.write({
            'addin_data': base64.b64encode(addin_data),
            'file_name': self.excel_add_in_name,
            'has_data': True
        })
        self._add_log_entry('Excel Add-in download prepared ({} bytes)'.format(len(addin_data)))
        return {
            'name': 'Download Excel Add-in',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'bi.sql.excel.addinfile.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self._context,
            'nodestroy': True,
        }
