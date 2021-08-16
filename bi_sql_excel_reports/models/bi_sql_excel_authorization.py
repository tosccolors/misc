# -*- coding: utf-8 -*-
# Copyright (C) 2021 - Today: Magnus (http://www.magnus.nl)
# @author: Vincent Verheul (v.verheul@magnus.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import SUPERUSER_ID
# from odoo.osv import expression

OBJ = None  # reference to bi.sql.excel.report model

_logger = logging.getLogger(__name__)


def set_model_ref(bi_sql_excel_report_model):
    """ Initialize global variable OBJ which references the calling model """
    global OBJ
    OBJ = bi_sql_excel_report_model


def object_attribute_value(obj, attr_stack):
    """ Get the attribute value of the object which may be an attribute of an underlying object
        when the field_stack list contains more than one attribute name. Works left to right within attr_stack. """
    if len(attr_stack) > 1:
        obj = getattr(obj, attr_stack[0])
        return object_attribute_value(obj, attr_stack[1:])
    return getattr(obj, attr_stack[0])


def user_params(user_model_attr):
    """ Pass a string value for user_model_attr after 'user.' as in the domain string,
        returns the actual user parameter value(s) """
    user_model = OBJ.env['res.users']
    user_record = user_model.search([('id', '=', OBJ.env.user.id)])
    attr_stack = user_model_attr.split('.')
    return object_attribute_value(user_record, attr_stack)


def convert_domain_tpl(tuple_str):
    """ Convert a domain-tuple as a string to a tuple object and handle references to the user object """
    lst = tuple_str.split(',')
    assert len(lst) == 3
    look_for = 'user.'
    start_position = lst[2].find(look_for)
    if -1 < start_position < 2:
        attributes = lst[2][start_position + len(look_for):-1]
        if lst[2][:1] == '[':
            lst[2] = [user_params(attributes)]
        elif lst[2][:1] == '(':
            lst[2] = tuple(user_params(attributes))
        else:
            lst[2] = user_params(attributes)
    return tuple(lst)


def convert_domain_str(domain_str):
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
                domain_lst.append(convert_domain_tpl(tuple_str))
                tuple_str = ''
                within_tuple = False
            else:
                tuple_str = ','.join((tuple_str, part))
    return domain_lst


def valid_domain_fields(column_names, domain, model_name):
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


def get_authorization_domain(model_name):
    """ Get the domain string as defined for 'Rule Definition' on the security tab of BI SQL Views """
    technical_name = model_name[14:] if model_name[:13] == 'x_bi_sql_view' else model_name
    bi_sql_view_model = OBJ.env['bi.sql.view']
    sql_views = bi_sql_view_model.search([('technical_name', '=', technical_name)])
    model_domain = []
    if len(sql_views) == 1:
        assert model_name == sql_views[0].model_name
        model_domain = sql_views[0].domain_force
    return model_domain


def get_authorization_filter(caller_object, model_name, column_names):
    """ Convert the domain string of the BI SQL Views query to an SQL where clause.
        caller_object is a recordset object only used to have access to .env
        model_name is the model of the BI SQL Views query
        column_names ia a list of the column names of the BI SQL Views query """
    set_model_ref(caller_object)
    auth_filter_list = []
    if OBJ.env.user.id == SUPERUSER_ID:
        return auth_filter_list

    sql_domain = convert_domain_str(get_authorization_domain(model_name))
    if not sql_domain:
        return ''
    if not valid_domain_fields(column_names, sql_domain, model_name):
        return 'false'

    sql_qry_model = OBJ.env[model_name]
    try:
        auth_filter_qry = sql_qry_model._where_calc(sql_domain)
    except ValueError as err:
        err_message = 'Error in {} get_authorization_filter applying rule to '.format(str(OBJ)) + \
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
