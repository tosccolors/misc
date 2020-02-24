# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class TrackerWizard(models.TransientModel):
    _name = 'tracker.wizard'
    _description = 'Tracker Wizard'

    date_from = fields.Datetime('Valid From')
    date_to = fields.Datetime('Valid To')

    @api.model
    def default_get(self, fields):
        result = super(TrackerWizard, self).default_get(fields)
        ctx = self.env.context.copy()
        if 'active_model' in ctx and 'active_id' in ctx:
            obj = self.env[ctx.get('active_model')].browse(ctx.get('active_id'))
            result['date_from'] = obj.date_from
            result['date_to'] = obj.date_to
        return result

    @api.multi
    def action_update(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        if self.date_from > self.date_to:
            raise UserError(_("'Valid From' date can't be greater than 'Valid To' date"))
        relation_ref = ctx.get('relation_ref', False)
        if 'active_model' in ctx and 'active_id' in ctx:
            curr_obj = self.env[ctx.get('active_model')]
            obj = curr_obj.browse(ctx.get('active_id'))

            common_domain = [('model', '=', obj.model),('relation_model', '=', obj.relation_model)]
            if relation_ref:
                common_domain += [('model_ref', '=', obj.model_ref)]
            else:
                common_domain += [('relation_ref', '=', obj.relation_ref)]

            search_domain = common_domain + [('id', '!=', obj.id)]
            sec_latest = curr_obj.search(search_domain, order='id Desc', limit=1)

            if len(curr_obj.search(common_domain)) > 2:
                found = curr_obj.search(common_domain+[('id', 'not in', [obj.id, sec_latest.id])]+[('date_from', '<=', self.date_from),('date_to', '>=', self.date_from)])
                if found:
                    raise UserError(_('Date range already has an entry.'))

                if sec_latest.date_from <= self.date_from and self.date_from < obj.date_to:
                    sec_latest.date_to = self.date_from
                    obj.date_from = self.date_from
                    obj.date_to = self.date_to
                else:
                    raise UserError(
                        _('Date must be in between %s and %s.') % (sec_latest.date_from, sec_latest.date_to))

            else:
                if sec_latest:
                    if sec_latest.date_from <= self.date_from and self.date_from < obj.date_to:
                        sec_latest.date_to = self.date_from
                    else:
                        sec_latest.date_from = self.date_to
                        if sec_latest.date_to < self.date_to:
                            sec_latest.date_to = self.date_to
                obj.date_from = self.date_from
                obj.date_to = self.date_to

        return True
