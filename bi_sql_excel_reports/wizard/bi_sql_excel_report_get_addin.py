# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from odoo import api, fields, models, modules


class GetAddInFile(models.TransientModel):
    _name = 'bi.sql.excel.addinfile.wizard'

    excel_add_in_name = 'Odoo-reports.xlam'
    json_csv_mac_name = 'OdooJsonToCsvMac.exe'
    json_csv_win_name = 'OdooJsonToCsvWin.exe'

    addin_file_name = fields.Char(
        string='Excel Add-in file name',
        readonly=True)
    addin_data = fields.Binary(
        string='Excel Add-in file data',
        readonly=True,
        help='Download Excel Add-in for SQL Excel Reports')
    json_csv_win_file_name = fields.Char(
        string='Json to CSV (Windows) executable file name',
        readonly=True)
    json_csv_win_data = fields.Binary(
        string='Json to CSV (Windows) executable file data',
        readonly=True,
        help='Download Json to CSV (Windows) executable')
    json_csv_mac_file_name = fields.Char(
        string='Json to CSV (Mac) executable file name',
        readonly=True)
    json_csv_mac_data = fields.Binary(
        string='Json to CSV (Mac) executable file data',
        readonly=True,
        help='Download Json to CSV (Mac) executable')
    has_data = fields.Boolean(
        string='Data loaded',
        default=False,
        help='Indicates that the Excel Add-in has been loaded')

    @staticmethod
    def _get_addin_binary(binary_file_name):
        """ Get the Excel Add-in file from the source directory """
        file_path = modules.get_module_resource('bi_sql_excel_reports', 'excel_add_in', binary_file_name)
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
        addin_data = self._get_addin_binary(self.excel_add_in_name)
        self.write({
            'addin_file_name': self.excel_add_in_name,
            'addin_data': base64.b64encode(addin_data),
            'json_csv_win_file_name': self.json_csv_win_name,
            'json_csv_win_data': base64.b64encode(self._get_addin_binary(self.json_csv_win_name)),
            'json_csv_mac_file_name': self.json_csv_mac_name,
            'json_csv_mac_data': base64.b64encode(self._get_addin_binary(self.json_csv_mac_name)),
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
