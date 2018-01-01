# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import models, fields, api
from odoo import tools


class Task(models.Model):
    _inherit = 'external.file.task'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        translate=False,
        readonly=True
        )