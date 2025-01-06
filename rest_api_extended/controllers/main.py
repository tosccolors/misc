# -*- coding: utf-8 -*-
# Copyright (C) 2024 The Open Source Company (<https://www.tosc.nl>)

import odoo
from odoo.addons.rest_api.controllers import main
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)


def get_analytic_accountID(aa_code):
    aaObj = request.env['account.analytic.account']
    aaID = aaObj.sudo().search([('code', '=', aa_code)], limit=1)
    aaID = aaID and aaID.id or False
    return aaID

def get_countryID(rc_code):
    rcObj = request.env['res.country']
    rcID = rcObj.sudo().search([('code', '=', rc_code)], limit=1)
    rcID = rcID and rcID.id or False
    return rcID

def get_analyticDistribution(dist_code):
    AAdist = {}
    for aa, v in dist_code.items():
        aaID = get_analytic_accountID(aa)
        AAdist.update({aaID:v})
    return AAdist

def get_singleAnalyticDistribution(aa_code):
    AAdist = {}
    aaID = get_analytic_accountID(aa_code)
    AAdist.update({aaID:100})
    return AAdist

def convert_values_from_jdata_to_vals1(modelname, jdata, creating=True):
    cr, uid = request.cr, request.session.uid
    Model = request.env(cr, uid)[modelname]

    x2m_fields = [f for f in jdata if type(jdata[f]) == list]
    f_props = Model.fields_get(x2m_fields)

    vals = {}
    for field in jdata:
        val = jdata[field]
        if type(val) != list:
            # Analytic Account
            if field == 'analytic_account_code':
                vals['analytic_account_id'] = get_analytic_accountID(val)

            # Analytic Distribution (Multi)
            elif field == 'analytic_distribution_code':
                vals['analytic_distribution'] = get_analyticDistribution(val)

            # Analytic Distribution (Single)
            elif field == 'single_analytic_code':
                vals['analytic_distribution'] = get_singleAnalyticDistribution(val)

            # Country
            elif field == 'country_code':
                vals['country_id'] = get_countryID(val)
            else:
                vals[field] = val
        else:
            # x2many
            #
            # Sample for One2many field:
            # 'bank_ids': [{'acc_number': '12345', 'bank_bic': '6789'}, {'acc_number': '54321', 'bank_bic': '9876'}]
            vals[field] = []
            field_type = f_props[field]['type']
            # if updating of 'many2many'
            if (not creating) and (field_type == 'many2many'):
                # unlink all previous 'ids'
                vals[field].append((5,))

            for jrec in val:
                rec = {}
                for f in jrec:
                    # Analytic Distribution (Multi)
                    if f == 'analytic_distribution_code':
                        rec['analytic_distribution'] = get_analyticDistribution(jrec[f])

                    # Analytic Distribution (Single)
                    elif f == 'single_analytic_code':
                        rec['analytic_distribution'] = get_singleAnalyticDistribution(jrec[f])

                    # Analytic Account
                    elif f == 'analytic_account_code':
                        rec['analytic_account_id'] = get_analytic_accountID(jrec[f])

                    # Country
                    elif f == 'country_code':
                        rec['country_id'] = get_countryID(jrec[f])
                    else:
                        rec[f] = jrec[f]

                if field_type == 'one2many':
                    if creating:
                        vals[field].append((0, 0, rec))
                    else:
                        if 'id' in rec:
                            id = rec['id']
                            del rec['id']
                            if len(rec):
                                # update record
                                vals[field].append((1, id, rec))
                            else:
                                # remove record
                                vals[field].append((2, id))
                        else:
                            # create record
                            vals[field].append((0, 0, rec))

                elif field_type == 'many2many':
                    # link current existing 'id'
                    vals[field].append((4, rec['id']))
    return vals

#Overridden:
main.convert_values_from_jdata_to_vals = convert_values_from_jdata_to_vals1

