# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError

class DataTrackThread(models.AbstractModel):
    _name = 'data.track.thread'

    model_track_ids = fields.One2many('data.time.tracker', 'model_ref', string='Model Tracker', domain=lambda self: [('model', '=', self._name)], auto_join=True)
    relation_track_ids = fields.One2many('data.time.tracker', 'relation_ref', string='Co-Model Tracker', domain=lambda self: [('relation_model', '=', self._name)], auto_join=True)

    @api.model
    def fetch_config(self):
        config = self.env['data.tracker.config'].search([('model_id.model', '=', self._name)])
        return config

    @api.model
    def _track_data(self, track_config, values, method='write'):
        for config in track_config:
            if config.field_id.name in values:
                data_tracker = self.env['data.time.tracker']
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if config.field_id.ttype == 'many2many':
                    for obj in self:
                        dic = {}
                        if config.model_id.model == self._name:
                            sdomain = [('model', '=', self._name), ('relation_model', '=', config.relation_model),
                                       ('model_ref', '=', obj.id), ('date_to', '=', '9999-12-31 00:00:00'),
                                       ('type_many2many', '=', True)]
                            #update date, if all values removed from many2many
                            if values[config.field_id.name] and not values[config.field_id.name][0][2] and obj[config.field_id.name].ids:
                                sdomain += [('relation_ref', 'in', obj[config.field_id.name].ids)]
                                trackObj = data_tracker.search(sdomain, limit=1)
                                trackObj.write({'date_to': current_date})
                            else:
                                #get new many2many ids
                                newRefIds = list(
                                    set(values[config.field_id.name][0][2]) - set(obj[config.field_id.name].ids)) if values[
                                    config.field_id.name] else []

                                # get removed many2many ids
                                unlinkRefIds = list(
                                    set(obj[config.field_id.name].ids)- set(values[config.field_id.name][0][2])) if values[config.field_id.name] else []
                                if unlinkRefIds:
                                    sdomain += [('relation_ref', 'in', unlinkRefIds)]
                                    trackObj = data_tracker.search(sdomain, limit=1)
                                    trackObj.write({'date_to': current_date})

                                dic['model'] = config.model_id.model
                                dic['relation_model'] = config.relation_model
                                dic['model_ref'] = obj.id
                                dic['type_many2many'] = True
                                dic['date_from'] = current_date
                                dic['date_to'] = '9999-12-31 00:00:00'
                                for refId in newRefIds:
                                    dic['relation_ref'] = refId
                                    data_tracker.create(dic)

                if config.field_id.ttype == 'many2one':
                    for obj in self:
                        dic = {}
                        if config.model_id.model == self._name:
                            fieldval = obj[config.field_id.name]
                            sdomain = [('model', '=', self._name), ('relation_model', '=', config.relation_model), ('model_ref', '=', obj.id), ('date_to', '=', '9999-12-31 00:00:00'), ('type_many2many', '=', False)]
                            trackObj = data_tracker.search(sdomain, limit=1)
                            trackObj.write({'date_to': current_date})
                            if fieldval and fieldval.id:
                                dic['model'] = config.model_id.model
                                dic['relation_model'] = config.relation_model
                                dic['model_ref'] = obj.id
                                dic['relation_ref'] = obj[config.field_id.name].id if method == 'create' else values[config.field_id.name]
                                dic['date_from'] = current_date
                                dic['date_to'] = '9999-12-31 00:00:00'
                                if dic['relation_ref']:
                                    data_tracker.create(dic)
                            elif not trackObj and not (fieldval and fieldval.id) and method == 'write' and values[config.field_id.name]:
                                dic['model'] = config.model_id.model
                                dic['relation_model'] = config.relation_model
                                dic['model_ref'] = obj.id
                                dic['relation_ref'] = values[config.field_id.name]
                                dic['date_from'] = current_date
                                dic['date_to'] = '9999-12-31 00:00:00'
                                if dic['relation_ref']:
                                    data_tracker.create(dic)
                    return True

    @api.model
    def create(self, values):
        res_id = super(DataTrackThread, self).create(values)
        track_config = self.fetch_config()
        res_id._track_data(track_config, values, 'create')
        return res_id

    @api.multi
    def write(self, values):
        if 'timeFaceCronUpdate' in self.env.context:
            self.remove_duplicates()
            return super(DataTrackThread, self).write(values)
        track_config = self.fetch_config()
        self._track_data(track_config, values, 'write')
        return super(DataTrackThread, self).write(values)

    def remove_duplicates(self):
        msg = self.env['mail.message']
        sqlop = 'IN'
        Ids = tuple(self.ids)
        if len(Ids) == 1:
            sqlop = '='
            Ids = Ids[0]
        list_query = (""" 
                SELECT  array_agg(id order by id desc)
                FROM mail_message
                WHERE res_id {0} {1} AND model = '{2}'
                GROUP BY date, res_id;
            """.format(
                sqlop,
                Ids,
                str(self._name)
        ))
        self.env.cr.execute(list_query)
        result = self.env.cr.fetchall()
        unlink_ids = []
        for res in result:
            msgIds = res[0]
            if len(msgIds) > 1:
                unlink_ids += msgIds[0:-1]
        if unlink_ids:
            msg = msg.browse(unlink_ids)
            msg.unlink()
        return True

class DataTrackerConfig(models.Model):
    _name = 'data.tracker.config'
    _description = 'Data Tracker Configuration'
    _rec_name = 'model_id'

    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', required=True, index=True)
    field_id = fields.Many2one('ir.model.fields', string='Tracking Field', required=True, index=True)
    relation_model = fields.Char(related='field_id.relation', string='Relational Model', required=True, index=True)

    def check_unique(self):
        pass

    @api.model
    def create(self, values):
        config = self.search([('model_id', '=', values['model_id']), ('field_id', '=', values['field_id'])])
        if config:
            raise UserError(_('Configuration already define for %s and field %s')%(config.model_id.model, config.field_id.name))
        return super(DataTrackerConfig, self).create(values)

    @api.multi
    def write(self, values):
        self.ensure_one()
        model = values['model_id'] if 'model_id' in values else self.model_id.id
        field = values['field_id'] if 'field_id' in values else self.field_id.id
        config = self.search([('model_id', '=', model), ('field_id', '=', field), ('id', '!=', self.id)])
        if config:
            raise UserError(
                _('Configuration already define for %s and field %s') % (config.model_id.model, config.field_id.name))
        return super(DataTrackerConfig, self).write(values)

class DataTimeTracker(models.Model):
    _name = 'data.time.tracker'
    _description = 'Data Tracker'
    _rec_name = 'model'

    @api.depends('model_ref', 'relation_ref')
    def _get_reference(self):
        for obj in self:
            if obj.model:
                model_obj = self.env[obj.model].browse(obj.model_ref).name_get()
                obj.model_name = model_obj and model_obj[0][1] or ''
            if obj.relation_model:
                rel_model_obj = self.env[obj.relation_model].browse(obj.relation_ref).name_get()
                obj.relation_model_name = rel_model_obj and rel_model_obj[0][1] or ''

    model = fields.Char('Parent Model', index=True)
    relation_model = fields.Char('Co-Model', index=True)
    model_ref = fields.Integer('Model Ref# ID', index=True)
    relation_ref = fields.Integer('Co-model Ref# ID', index=True)
    date_from = fields.Datetime('Valid From')
    date_to = fields.Datetime('Valid To')
    model_name = fields.Char(compute ='_get_reference', string="Model Ref#")
    relation_model_name = fields.Char(compute ='_get_reference', string="Co-model Ref#")
    type_many2many = fields.Boolean()

    @api.multi
    def action_open_view(self):
        self.ensure_one()
        active_model = self.env.context.get('active_model', '')
        res_id = False
        model = ''
        if active_model:
            if self.model == active_model:
                res_id = self.relation_ref
                model = self.relation_model
            elif self.relation_model == active_model:
                res_id = self.model_ref
                model = self.model
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': model,
                'target': 'current',
                'res_id': res_id,
                'type': 'ir.actions.act_window'
            }
        return True

    @api.multi
    def remove(self):
        self.ensure_one()
        ctx = self.env.context.copy()
        relation_ref = ctx.get('relation_ref', False)
        search_domain = [('id', '!=', self.id), ('model', '=', self.model), ('relation_model', '=', self.relation_model)]
        if relation_ref:
            search_domain += [('model_ref', '=', self.model_ref)]
        else:
            search_domain += [('relation_ref', '=', self.relation_ref)]
        sec_latest = self.search(search_domain, order='id Desc', limit=1)
        sec_latest.date_to = '9999-12-31 00:00:00'
        self.unlink()
        return True