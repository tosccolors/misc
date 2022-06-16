# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class Project(models.Model):
    _inherit = "project.project"

    code = fields.Char('Project Code')

    @api.multi
    def name_get(self):
        return [(v.id, "%s%s" % (v.code + '-' if v.code else '', v.name)) for v in self]


class Tasks(models.Model):
    _inherit = 'project.task'

    def link_project2task(self):
        " Method called in server action"

        projects = {}
        for p in self.env['project.project'].sudo().search([]):
            if not p.code: continue
            projects[p.code] = p.id

        for rec in self:
            for code, pid in projects.items():
                try:
                    if code.upper() in rec.name.upper():
                        rec.sudo().write({'project_id': pid})
                        break
                except:
                    continue

