# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from collections import OrderedDict
from odoo import SUPERUSER_ID
# from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ReportAuthorization:
    """ Check queries using the authorizations defined for each query in the bi.sql.view model """

    def __init__(self, caller_object):
        """ :param caller_object is a reference to the bi_sql_excel_report object (to use its .env property)
            nodes is a dictionary with the report tree hierarchy nodes, excluding the reports which are the 'leaves' """
        self.parent_object = caller_object
        self.sql_view_prefix = 'x_bi_sql_view'

    def __repr__(self):
        clsname = self.__class__.__name__
        return '{}()'.format(clsname)

    def is_super_user(self):
        """ True when the logged-on user is a super user """
        return self.parent_object.env.user.id == SUPERUSER_ID

    def _object_attribute_value(self, obj, attr_stack):
        """ Get the attribute value of the object which may be an attribute of an underlying object
            when the field_stack list contains more than one attribute name. Works left to right within attr_stack. """
        if len(attr_stack) > 1:
            obj = getattr(obj, attr_stack[0])
            return self._object_attribute_value(obj, attr_stack[1:])
        return getattr(obj, attr_stack[0])

    def _user_params(self, user_model_attr):
        """ Pass a string value for user_model_attr after 'user.' as in the domain string,
            returns the actual user parameter value(s) """
        user_model = self.parent_object.env['res.users']
        user_record = user_model.search([('id', '=', self.parent_object.env.user.id)])
        attr_stack = user_model_attr.split('.')
        return self._object_attribute_value(user_record, attr_stack)

    def _convert_domain_tpl(self, tuple_str):
        """ Convert a domain-tuple as a string to a tuple object and handle references to the user object """
        lst = tuple_str.split(',')
        assert len(lst) == 3
        look_for = 'user.'
        start_position = lst[2].find(look_for)
        if -1 < start_position < 2:
            attributes = lst[2][start_position + len(look_for):-1]
            if lst[2][:1] == '[':
                lst[2] = [self._user_params(attributes)]
            elif lst[2][:1] == '(':
                lst[2] = tuple(self._user_params(attributes))
            else:
                lst[2] = self._user_params(attributes)
        return tuple(lst)

    def _convert_domain_str(self, domain_str):
        """ Convert a domain as a string to a Python list with strings and tuples """
        domain_str = domain_str.replace("'", '')
        domain_lst = []
        if not (domain_str[:1] == '[' and domain_str[-1:] == ']'):
            return domain_lst
        parts = domain_str.split(',')
        parts[0] = parts[0][1:]
        parts[-1] = parts[-1][:-1]
        for seq, part in enumerate(parts):
            parts[seq] = parts[seq].strip()
        within_tuple = False
        tuple_str = ''
        for part in parts:
            if not within_tuple:
                if part[:1] == '(':
                    tuple_str = part[1:]
                    within_tuple = True
                else:
                    domain_lst.append(part)
            else:
                if part[-1:] == ')':
                    tuple_str = ','.join((tuple_str, part[:-1]))
                    domain_lst.append(self._convert_domain_tpl(tuple_str))
                    tuple_str = ''
                    within_tuple = False
                else:
                    tuple_str = ','.join((tuple_str, part))
        return domain_lst

    @staticmethod
    def _valid_domain_fields(column_names, domain, model_name):
        """ Check if the field names referenced in the domain exist in the model's column names """
        missing_fields = set()
        for part in domain:
            if type(part) == tuple:
                if part[0] not in column_names:
                    missing_fields.add(part[0])
        if missing_fields:
            raise ValueError('SQL View %s security rule field(s) %s do not exist in view' %
                             (model_name, str(tuple(missing_fields))))
        return True

    def _query_techical_name_suffix(self, model_name):
        """ Remove 'x_bi_sql_view.' from the query model name to obtain the suffix """
        return model_name[14:] if model_name[:13] == self.sql_view_prefix else model_name

    def _get_authorization_domain(self, model_name):
        """ Get the domain string as defined for 'Rule Definition' on the security tab of BI SQL Views """
        technical_name = self._query_techical_name_suffix(model_name)
        bi_sql_view_model = self.parent_object.env['bi.sql.view']
        sql_views = bi_sql_view_model.sudo().search([('technical_name', '=', technical_name)])
        model_domain = []
        if len(sql_views) == 1:
            assert model_name == sql_views[0].model_name
            model_domain = sql_views[0].domain_force
        return model_domain

    def get_authorization_filter(self, model_name, column_names):
        """ Convert the domain string of the BI SQL Views query to an SQL where-clause.
            :param model_name is the model of the BI SQL Views query
            :param column_names is a list of the column names of the BI SQL Views query """
        auth_filter_list = []
        if self.is_super_user():
            return auth_filter_list

        sql_domain = self._convert_domain_str(self._get_authorization_domain(model_name))
        if not sql_domain:
            return ''
        if not self._valid_domain_fields(column_names, sql_domain, model_name):
            return 'false'

        sql_qry_model = self.parent_object.env[model_name]
        try:
            auth_filter_qry = sql_qry_model._where_calc(sql_domain)
        except ValueError as err:
            err_message = 'Error in {} get_authorization_filter applying rule to '.format(str(model_name)) + \
                          'model {}: {}'.format(model_name, err.message)
            logging.error(err_message)
        else:
            auth_filter_list = auth_filter_qry.where_clause
            auth_filter_pars = auth_filter_qry.where_clause_params
            for seq, fltr in enumerate(auth_filter_list):
                auth_filter_list[seq] = fltr.replace(auth_filter_qry.tables[0] + '.', '')
            assert len(auth_filter_list) == 1
            auth_filter_list[0] = auth_filter_list[0] % tuple(auth_filter_pars)
        return auth_filter_list[0] if auth_filter_list else []

    def get_authorized_queries(self, query_name_wildcard=''):
        """ Match the user's authorization groups to the authorization groups for all query names (technical name)
            The query authorization groups are defined in 'Allowed Groups' on the security tab of BI SQL Views.
            Returns a list of allowed queries (technical name) optionally filtered by query_name_wildcard.
            :param query_name_wildcard is an optional filter on the query technical names """
        bi_sql_view_model = self.parent_object.env['bi.sql.view']
        if not query_name_wildcard:
            sql_views = bi_sql_view_model.sudo().search([])
        else:
            sql_views = bi_sql_view_model.sudo().search([('technical_name', 'like', query_name_wildcard)])
        allowed_queries = []
        for sql_view in sql_views:
            query_authorized = False
            for grp in sql_view.group_ids:
                if self.parent_object.env.user in grp.users:
                    query_authorized = True
                    break
            if query_authorized:
                allowed_queries.append(self._query_techical_name_suffix(sql_view.model_name))
        return allowed_queries

    def _hierarchy_node_rpt_count(self, data, nodes, seq):
        """ Count the number of authorized reports per hierarchy level: updates nodes """
        for line in data:
            if line['sequence'] <= seq or line['is_select_index']:
                continue
            if line['is_group']:
                grp_seq = line['sequence']
                self._hierarchy_node_rpt_count(data, nodes, grp_seq)
                if nodes[grp_seq]['parent'] > 0:
                    nodes[nodes[grp_seq]['parent']]['rpt_cnt'] += nodes[grp_seq]['rpt_cnt']
                break
            else:
                if seq > 0 and line['active']:
                    nodes[seq]['rpt_cnt'] += 1

    @staticmethod
    def _hierarchy_set_parents(nodes):
        """ Set a reference to the parent node within the report hierarchy for lower level hierarchy levels """
        maxlevel = max(node['group_level'] for node in nodes.values())
        curr_hierarchy = [0 for _ in range(-1, maxlevel)]
        prevlevel = -1
        for seq, node in nodes.items():
            node['parent'] = curr_hierarchy[node['group_level'] - 1] if node['group_level'] >= prevlevel else 0
            if node['group_level'] != prevlevel:
                curr_hierarchy[node['group_level']] = seq
                prevlevel = node['group_level']

    def hierarchy_filter_node_auth(self, report_def):
        """ Hierarchy nodes within the report hierarchy are (potentially) filtered-out based on
            (un)authorised reports on the 'leaves' of the tree.
            :param report_def is the contents of report definitions (list of dicts) """
        nodes = OrderedDict()
        for idx, line in enumerate(report_def):
            if line['is_group'] and not line['is_select_index']:
                nodes[line['sequence']] = {'data_index': idx, 'group_level': line['group_level'],
                                           'name': line['name'], 'parent': 0, 'rpt_cnt': 0}
        if nodes:
            self._hierarchy_set_parents(nodes)
            self._hierarchy_node_rpt_count(report_def, nodes, 0)
            for node in nodes.values():
                if node['rpt_cnt'] == 0:
                    report_def[node['data_index']]['active'] = False
            report_def = [line for line in report_def if line['active']]
        return report_def
