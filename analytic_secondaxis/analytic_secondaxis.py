# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Camptocamp SA (http://www.camptocamp.com)
# All Right Reserved
#
# Author : Joel Grand-guillaume (Camptocamp)
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

from odoo import fields, models, api
import odoo.addons.decimal_precision as dp


class ProjectActivityAl(models.Model):

    """Class that inhertis osv.osv and add 2nd analytic axe to account analytic
    lines.
    The _name is kept for previous version compatibility (project.activity_al).
    """
    # Keep that name for back -patibility
    _name = "project.activity_al"
    _description = "Second Analytical Axes"

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        context = self._context or {}
        acc_ids = []

        # TODO: FIXME:
        # Field 'date' doesn't exist, hence commented the below code
        # if context.get('from_date', False):
        #     args.append(['date', '>=', context['from_date']])
        # if context.get('to_date', False):
        #     args.append(['date', '<=', context['to_date']])

        if context.get('account_id', False):
            aa_obj = self.env['account.analytic.account']
            account_id = aa_obj.browse(context.get('account_id', False))
            # take the account wich have activity_ids
            acc_who_matters = self._get_first_AA_wich_have_activity(account_id)
            if acc_who_matters:
                for i in acc_who_matters.activity_ids:
                    acc_ids.append(i.id)
                args.append(('id', 'in', acc_ids))

        return super(ProjectActivityAl, self).search(args, offset, limit, order, count=count)

    @api.model
    def _get_first_AA_wich_have_activity(self, account):
        """Return browse record list of activities
           of the account which have an activity set
           (goes bottom up, child, then parent)
        """
        if account.activity_ids:
            return account
        else:
            if account.parent_id:
                return self._get_first_AA_wich_have_activity(account.parent_id)
            else:
                return False


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """ Ovveride of osv.osv name serach function that do the search
            on the name of the activites """
        if not args:
            args = []

        account = self.search([('code', '=', name)] + args, limit=limit)
        if not account:
            account = self.search([('name', 'ilike', '%%%s%%' % name)] + args, limit=limit)
        if not account:
            account = self.search([] + args, limit=limit)

        # For searching in parent also
        if not account:
            account = self.search([('name', 'ilike', '%%%s%%' % name)] + args, limit=limit)
            newacc = account
            while newacc:
                newacc = self.search([('parent_id', 'in', newacc)] + args, limit=limit)
                account += newacc

        return account.name_get()

    @api.model
    def _compute_level_tree(self, child_ids, res, field_names):
        def recursive_computation(account_id, res):
            currency_obj = self.env['res.currency']
            account = self.browse(account_id)

            for son in account.child_ids:

                res = recursive_computation(son.id, res)
                # --added by deep
                if account.id not in res.keys():
                    res.update({account.id: {'credit': 0.0, 'balance': 0.0, 'quantity': 0.0, 'debit': 0.0}})
                if son.id not in res.keys():
                    res.update({son.id: {'credit': 0.0, 'balance': 0.0, 'quantity': 0.0, 'debit': 0.0}})

                for field in field_names:
                    if (account.currency_id.id == son.currency_id.id or field == 'quantity'):
                        res[account.id][field] += res[son.id][field]
                    else:
                        res[account.id][field] += son.currency_id.compute(res[son.id][field], account.currency_id)
            return res

        for account in self:
            if account.id not in child_ids:
                continue
            res = recursive_computation(account.id, res)
        return res

    @api.one
    def _debit_credit_bal_qtty(self):
        self.debit = 0.00
        self.credit = 0.00
        self.balance = 0.00
        self.quantity = 0.00

        cr, context = self._cr, self._context

        res = {}
        child_ids = tuple(self.search([('parent_id', 'child_of', self.ids)]).ids)

        where_date = ''
        where_clause_args = [tuple(child_ids)]
        if context.get('from_date', False):
            where_date += " AND l.date >= %s"
            where_clause_args += [context['from_date']]
        if context.get('to_date', False):
            where_date += " AND l.date <= %s"
            where_clause_args += [context['to_date']]

        cr.execute("""
              SELECT a.id,
                     sum(CASE WHEN l.amount > 0 THEN l.amount ELSE 0.0 END) as debit,
                     sum(CASE WHEN l.amount < 0 THEN -l.amount ELSE 0.0 END) as credit,
                     COALESCE(SUM(l.amount),0) AS balance,
                     COALESCE(SUM(l.unit_amount),0) AS quantity
              FROM project_activity_al a
              LEFT JOIN account_analytic_line l ON (a.id = l.activity)
              WHERE a.id IN %s
              """ + where_date + """
              GROUP BY a.id""", where_clause_args)

        for ac_id, debit, credit, balance, quantity in cr.fetchall():
            res[ac_id] = {'debit': debit, 'credit': credit,
                          'balance': balance, 'quantity': quantity}
        res2 = self._compute_level_tree(child_ids, res, ['debit', 'credit', 'balance', 'quantity'])

        for id, vals in res2.iteritems():
            case = self.browse(id)
            case.update(vals)
        return res2

    @api.model
    def _default_company(self):
        user = self.env['res.users'].browse(self._uid)
        if user.company_id:
            return user.company_id.id
        comps = self.env['res.company'].search([('parent_id', '=', False)]).ids
        return comps and comps[0] or False

    @api.model
    def _get_default_currency(self):
        user = self.env['res.users'].browse(self._uid)
        return user.company_id.currency_id.id

    # activity code
    code = fields.Char('Code', required=True, size=64)
    # name of the code
    name = fields.Char('Activity', required=True, size=64, translate=True)
    # parent activity
    parent_id = fields.Many2one('project.activity_al', 'Parent activity')

    # link to account.analytic account
    project_ids = fields.Many2many('account.analytic.account',
        'proj_activity_analytic_rel', 'activity_id', 'analytic_id', 'Concerned Analytic Account')

    # link to the children activites
    child_ids = fields.One2many('project.activity_al', 'parent_id', 'Childs Activities')

    balance = fields.Float(compute='_debit_credit_bal_qtty', string='Balance',
        digits=dp.get_precision('Account'))

    debit = fields.Float(compute='_debit_credit_bal_qtty',
        string='Debit', digits=dp.get_precision('Account'))

    credit = fields.Float(compute='_debit_credit_bal_qtty',
        string='Credit', digits=dp.get_precision('Account'))

    quantity = fields.Float(compute='_debit_credit_bal_qtty', string='Quantity')

    currency_id = fields.Many2one('res.currency', string='Activity currency', required=True, default=_get_default_currency)

    company_id = fields.Many2one('res.company', string='Company', required=False, default=_default_company)


class AnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    # Link activity and project
    activity_ids = fields.Many2many('project.activity_al',
        'proj_activity_analytic_rel', 'analytic_id', 'activity_id', 'Related activities')



class AnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    activity = fields.Many2one('project.activity_al', 'Activity')
