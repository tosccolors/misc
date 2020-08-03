# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    perform_posting_by_line = fields.Boolean(string="Perform Posting by Line", default=False)
    use_description_as_reference = fields.Boolean(string="Use description as reference")
    reversal_via_sql = fields.Boolean(string="Reversal Via Sql", default=False)
