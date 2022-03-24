# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from odoo import api, fields, models, modules
from ..models.bi_sql_excel_report import BiSqlExcelReport


class GetAddInFile(models.TransientModel):
    _name = 'bi.sql.excel.addinfile.wizard'
    excel_add_in_name = 'Odoo-reports.xlam'
    excel_add_in_vers = '0.0'
    json_csv_name = {'MacOS': 'OdooJsonToCsv', 'Windows': 'OdooJsonToCsv.exe'}
    user_sys_code = {'MacOS': 'mac', 'Windows': 'win'}

    user_sys = fields.Char(
        string='User operating system',
        default='',
        help="Operating system of the user's computer")
    addin_win_file_name = fields.Char(
        string='Excel Add-in file name for Windows',
        readonly=True)
    addin_win_data = fields.Binary(
        string='Excel Add-in file data for Windows',
        readonly=True,
        help='Download Excel Add-in for SQL Excel Reports')
    addin_mac_file_name = fields.Char(
        string='Excel Add-in file name for Mac',
        readonly=True)
    addin_mac_data = fields.Binary(
        string='Excel Add-in file data for Mac',
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

    def _add_log_entry(self, message, line='0'):
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

    def _write_record(self):
        """ Write data to the wizard table, depending on selected user system: must be separate fields, even when the
            contents is the same since a field cannot be displayed more than once in a form """
        self.excel_add_in_vers = BiSqlExcelReport.add_in_latest_ver
        addin_data = self._get_addin_binary(self.excel_add_in_name)
        usys = self.user_sys_code[self.user_sys]
        self.write({
            'user_sys': self.user_sys,
            'addin_%s_file_name' % usys: self.excel_add_in_name,
            'addin_%s_data' % usys: base64.b64encode(addin_data),
            'json_csv_%s_file_name' % usys: self.json_csv_name[self.user_sys],
            'json_csv_%s_data' % usys: base64.b64encode(self._get_addin_binary(self.json_csv_name[self.user_sys])),
            'has_data': True})

    def _open_download_form(self):
        """ Call form to display prepared record in wizard table """
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

    def _create_log_entry(self):
        log_msg = 'Excel Add-in version {} download prepared for {}'.format(self.excel_add_in_vers, self.user_sys)
        self._add_log_entry(message=log_msg, line=self.excel_add_in_vers)

    def _prepare_addin_file(self):
        """ Prepare the Excel Add-in for download and (re-) open the form with data loaded """
        self._write_record()
        self._create_log_entry()
        return self._open_download_form()

    @api.multi
    def prepare_addin_file_win(self):
        """ Prepare the Excel Add-in for a user on Windows """
        self.user_sys = 'Windows'
        return self._prepare_addin_file()

    @api.multi
    def prepare_addin_file_mac(self):
        """ Prepare the Excel Add-in for a user on MacOS """
        self.user_sys = 'MacOS'
        return self._prepare_addin_file()
