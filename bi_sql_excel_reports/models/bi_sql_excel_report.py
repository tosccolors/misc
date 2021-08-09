# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from datetime import datetime
import logging
from odoo import fields, models, api
# from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class BiSqlExcelReport(models.Model):
    _name = 'bi.sql.excel.report'
    _order = 'sequence, id'

    bi_sql_view_model = None
    user_model = None

    active = fields.Boolean('Active', default=True)

    field_ids = fields.One2many(
        comodel_name='bi.sql.excel.report.field',
        inverse_name='report_id',
        string='Report fields')

    sequence = fields.Integer(
        string='Sequence',
        required=True,
        help="Determines the sequence of the reports")

    # _sql_constraints = [
    #     ('sequence_uniq',
    #      'UNIQUE (sequence)',
    #      'The sequence must be unique.')
    #     ]

    name = fields.Char(
        string='Report name',
        required=True,
        help="Hierarchy (sub)group name or report name")

    short_name = fields.Char(
        string='Report short name',
        help="Unique short name used as worksheet name")

    description = fields.Text(
        string='Report description',
        help="Excel report long description")

    is_group = fields.Boolean(
        string='Is Group',
        default=False,
        help="Indicate that this is a group, not a report")

    group_level = fields.Integer(
        string='Group level',
        help="Use groups to build a hierarchy under which you place your reports, " +
             "specify the level if you use groups within groups")

    is_select_index = fields.Boolean(
        string='Is Select Index',
        help="Is a selection index to use as global filter in reports")

    query_name = fields.Char(
        string='SQL View name',
        help="SQL View technical name which is the data source for the Excel report")

    filter_on_user = fields.Boolean(
        string='Filter on current user',
        default=False,
        help="Add a filter on records that contain the current user")

    table_row = fields.Integer(
        string='Table top-left row',
        default=5)

    table_col = fields.Integer(
        string='Table top-left column',
        default=20)

    table_row_tot = fields.Boolean(
        string='Table grand tot rows',
        default=True)

    table_col_tot = fields.Boolean(
        string='Table grand tot cols',
        default=True)

    chart_type = fields.Char(
        string='Excel chart type',
        help="Excel chart type (in English) or leave blank when no chart required")

    chart_left = fields.Integer(
        string='Chart left',
        help='Chart position (points): left',
        default=3)

    chart_top = fields.Integer(
        string='Chart top',
        help='Chart position (points): top',
        default=8)

    chart_width = fields.Integer(
        string='Chart width',
        help='Chart position (points): width',
        default=730)

    chart_height = fields.Integer(
        string='Chart height',
        help='Chart position (points): height',
        default=401)

    chart_scale = fields.Float(
        string='Chart y-scale',
        help='Chart y-scale max value (1 = 100%), not applicable when zero',
        default=0.0)

    def get_authorization_filter(self, model_name):
        if not self.user_model:
            self.user_model = self.env['res.users']
        if not self.bi_sql_view_model:
            self.bi_sql_view_model = self.env['bi.sql.view']
        if model_name[:13] == 'x_bi_sql_view':
            model_name = '.'.join((model_name[:13], model_name[14:]))
        sql_view_id = self.bi_sql_view_model.search([('technical_name', '=', model_name)])
        sql_view_rec = self.bi_sql_view_model.browse(sql_view_id)
        # todo: fetch auth domain from sql_qry_model
        args = ['|', ('x_company_id', 'child_of', self.user_model.company_id.ids), ('x_company_id', '=', False)]
        sql_qry_model = self.env[model_name]
        auth_filter_qry = sql_qry_model._where_calc(args)
        auth_filter_list = auth_filter_qry.where_clause
        for seq, fltr in enumerate(auth_filter_list):
            auth_filter_list[seq] = fltr.replace(auth_filter_qry.tables[0] + '.', '')
        return auth_filter_list

    def _exec_query(self, table_or_view, where_clause='', order_by_clause='', is_meta_data=False):
        """ Execute SQL query, selecting all columns and records matching the where clause (optional) """
        sql = 'SELECT * FROM ' + table_or_view
        sql += ' WHERE ' + where_clause if where_clause else ''
        sql += ' ORDER BY ' + order_by_clause if order_by_clause else ''
        # sql += ' LIMIT 100'

        auth_filter = ''
        if not is_meta_data:
            auth_filter = self.get_authorization_filter(table_or_view)
        print auth_filter

        err_msg = ''
        try:
            self.env.cr.execute(sql)
        except Exception as err:
            logging.info('%s _exec_query error reading table or view %s: %s', self._name, table_or_view, err)
            err_msg = err.message
            p = err_msg.find('\n')
            if p > -1:
                err_msg = u'error: ' + err_msg[:p]
            err_msg = err_msg.replace(u'"', u"'")
        return err_msg

    def _get_query_column_names(self, table_or_view):
        """ Get column names of the specified table or view. Returns the column names in a list. """
        data = []
        sql = "SELECT column_name FROM information_schema.columns " + \
              "WHERE table_name  = '" + table_or_view + "' order by ordinal_position"
        try:
            self.env.cr.execute(sql)
        except Exception as err:
            logging.info('% _get_query_column_names error reading table or view ' +
                         'column names %s: %s', self._name, table_or_view, err)
        else:
            for col_name in self.env.cr.fetchall():
                data.append(col_name[0])
        return data

    @staticmethod
    def _shorten_dates(header, data):
        """ Change date field contents into a format that Excel understands as a date """
        for field in header:
            if field[-4:] != 'date':
                continue
            date_ix = header.index(field)
            data = [[fld_val if ix != date_ix else str(fld_val)[:19]
                     for ix, fld_val in enumerate(row)] for row in data]
        return data

    def _get_meta_data(self, table_name, where_clause='', order_by_clause='', as_a_dict=True):
        """ Get the active contents of a meta data table, either as a list of dictionaries, a list of lists without
            header or a list of lists with a header. """
        header = self._get_query_column_names(table_name)
        err_msg = self._exec_query(table_name, where_clause, order_by_clause, is_meta_data=True)
        if err_msg:
            return err_msg
        data = self.env.cr.fetchall()
        if as_a_dict:
            data = [{col: dat for col, dat in zip(header, row)} for row in data]
        else:
            data = self._shorten_dates(header, data)
            header = [header]
            header.extend(data)
            data = header
        return data

    @api.model
    def get_module_version(self):
        """ Get the module version from the manifest """
        delim = '/' if '/' in __file__ else '\\'
        file_parts = __file__.split(delim)[:-2]
        file_parts.append('__manifest__.py')
        manifest_path = delim.join(file_parts)
        mod_version = '?'
        with open(manifest_path, 'r') as mf:
            mfdata = mf.read()
            start = mfdata.find('"version":')
            if start > -1:
                stop = mfdata.find('",', start + 10)
                if stop > -1:
                    mod_version = mfdata[start + 10: stop]
                    mod_version = mod_version.replace('"', '')
                    mod_version = mod_version.strip()
            print(mfdata)
        return mod_version

    @api.model
    def excel_add_in_compatible(self, user_machine_info):
        """ Called from the Excel add-in to check if its version is compatible with this Odoo module """
        if type(user_machine_info) != dict:
            return False
        expected_keys = ['os_version', 'excel_version', 'addin_version']
        info = {key: val for key, val in user_machine_info.items() if key in expected_keys}
        add_in_ver = info.get('addin_version')
        if type(add_in_ver) in (str, unicode) and add_in_ver.replace('.', '').isnumeric():
            add_in_ver = float(add_in_ver)
        if add_in_ver is None:
            add_in_ver = 0.0
        if add_in_ver < 0.3:
            return False
        return True

    @api.model
    def get_report_def_timestamp(self):
        """ Get the oldest update timestamp (write_date) of the active Excel report definitions """
        data = self._get_meta_data(table_name='bi_sql_excel_report', where_clause='active=True', as_a_dict=True)
        timestamp = '2000-01-01 00:00:00'
        if data and type(data) == list:
            timestamp = max([row['write_date'] for row in data])
            timestamp = timestamp[:19]
        return timestamp

    @api.model
    def get_report_definitions(self, as_a_dict=True):
        """ Get all active Excel report definitions as a list of dicts or
            as a list of lists (table) with the first row having the field names """
        return self._get_meta_data(table_name='bi_sql_excel_report', where_clause='active=True',
                                   order_by_clause='sequence', as_a_dict=as_a_dict)

    @api.model
    def get_report_layout_definitions(self, as_a_dict=True):
        """ Get all Excel report field definitions (for all reports) as a list of dicts or
            as a list of lists (table) with the first row having the field names """
        reports = self.get_report_definitions(as_a_dict=True)
        if not reports:
            return []
        rpt_seqs = {rpt['id']: rpt['sequence'] for rpt in reports}
        layouts = self._get_meta_data(table_name='bi_sql_excel_report_field',
                                      order_by_clause='report_id, sequence', as_a_dict=True)
        if type(layouts) != list:
            return layouts
        for layout in layouts:
            if layout[u'report_id'] in rpt_seqs:
                layout[u'report_seq'] = rpt_seqs[layout['report_id']]
            else:
                layout[u'report_seq'] = None
        layouts = [layout for layout in layouts if layout[u'report_seq'] is not None]
        if not as_a_dict:
            if layouts:
                header = [fld_name for fld_name in layouts[0].keys()]
                data = [[fld_val for fld_val in row.values()] for row in layouts]
                data = self._shorten_dates(header, data)
                rows = [header]
                rows.extend(data)
                layouts = rows
            else:
                layouts = []
        return layouts

    @api.model
    def get_report_data(self, report_seq, where_clause=''):
        """ Get the contents of the query associated with report_seq and return as
            a list of lists (table) with the first row having the field names """
        qry_not_found_msg = 'Error: No SQL View found for report code {}'.format(report_seq)
        sql = "SELECT query_name FROM bi_sql_excel_report WHERE sequence='" + str(report_seq) + "'"
        self.env.cr.execute(sql)
        try:
            query_name = self.env.cr.fetchone()[0]
        except Exception as err:
            logging.error('% get_report_data error ', self._name, err.message)
            return qry_not_found_msg

        if not query_name:
            return qry_not_found_msg
        query_name = 'x_bi_sql_view_' + query_name
        data = [self._get_query_column_names(query_name)]
        if not data or data == [[]]:
            return qry_not_found_msg
        del_first_columns = data[0][:5] == ['id', 'create_date', 'create_uid', 'write_date', 'write_uid']
        err_msg = self._exec_query(query_name, where_clause)
        if err_msg:
            return err_msg
        data.extend(self.env.cr.fetchall())
        if del_first_columns:
            data = [row[5:] for row in data]
        # cannot have plain brackets [] or curly brackets {} in a string as these are interpreted
        # in the Excel add-in logic as list and dict delimiters
        data = [[fld.replace(u'[', u"'['").replace(u']', u"']'").replace(u'{', u"'{'").replace(u'}', u"'}'")
                 if fld and type(fld) in (str, unicode) else fld for fld in row]
                for row in data]
        return data
