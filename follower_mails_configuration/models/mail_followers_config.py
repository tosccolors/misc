# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from odoo.exceptions import UserError

class MailFollowersConfig(models.Model):
    _name = 'mail.followers.config'
    _rec_name = 'company_id'

    company_id = fields.Many2one('res.company', 'Company', index=True)
    model_id = fields.Many2one('ir.model', string='Model', ondelete='cascade', help='Domain applied for selected model')
    value = fields.Boolean('Is customer?', help="Customer to notify mail.")
    complete_stop = fields.Boolean('Do not send any mails?', help="If true mail would not trigger")
    stop_track_visibility = fields.Boolean('Stop Track Visibility?', help="If true field onchange tracking would not be notified to customer via mail")

    @api.model
    def create(self, vals):
        if len(self.search([('company_id', '=', vals.get('company_id')), ('model_id','=',vals.get('model_id'))])) >= 1:
            raise UserError(_("Followers configuration already exists for same company"))
        return super(MailFollowersConfig, self).create(vals)

    @api.multi
    def write(self, vals):
        assert len(self.ids) == 1, "you can open only one configuration at a time"
        if vals.has_key('model_id') or vals.has_key('company_id'):
            if vals.has_key('company_id'):
                company_id = vals.get('company_id')
            else:
                company_id = self.company_id and self.company_id.id or False
            if company_id:
                if vals.has_key('model_id') and vals.get('model_id'):
                    model_id = vals.get('model_id')
                else:
                    model_id = self.model_id and self.model_id.id or False
                if self.search([('id', 'not in', self._ids), ('model_id', '=', model_id), ('company_id', '=', company_id)]):
                    raise UserError(_("Followers configuration already exists for same company"))
        return super(MailFollowersConfig, self).write(vals)

    def followers_config(self, model, res_id):
        company = self.env.user.company_id.id
        cmpy_field = self.env['ir.model.fields'].search(
            [('model_id.model', '=', model), ('ttype', '=', 'many2one'), ('relation', '=', 'res.company')], limit=1)
        if cmpy_field:
            company = self.env[model].browse(res_id)[cmpy_field.name].id
        if company:
            config_model_obj = self.search([('model_id.model', '=', model), ('company_id', '=', company)], limit=1)
            if not config_model_obj:
                config_model_obj = self.search([('model_id', '=', False), ('company_id', '=', company)], limit=1)
            return config_model_obj
        return self

    def followers_domain(self, model, res_id):
        domain = [('user_ids','!=',False)]
        # company = self.env.user.company_id.id
        # cmpy_field = self.env['ir.model.fields'].search([('model_id.model','=',model),('ttype','=','many2one'),('relation','=','res.company')], limit=1)
        # if cmpy_field:
        #     company = self.env[model].browse(res_id)[cmpy_field.name].id
        # if company:
        #     config_model_obj = self.search([('model_id.model','=',model),('company_id','=',company)], limit=1)
        #     if not config_model_obj:
        #         config_model_obj = self.search([('model_id', '=', False),('company_id','=',company)], limit=1)
        config_model_obj = self.followers_config(model, res_id)
        if config_model_obj:
            domain += [('customer', '=', config_model_obj.value)]
        return domain







