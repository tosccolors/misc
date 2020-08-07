# -*- coding: utf-8 -*-
# © 2013-2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    perform_posting_by_line = fields.Boolean(string="Experimental - Perform Posting by Line", default=False)
    use_description_as_reference = fields.Boolean(string="Use description as reference")
    reversal_via_sql = fields.Boolean(string="Experimental - Reversal Via Sql", default=False)
    perform_posting_by_line_jq = fields.Boolean(string="Perform Posting By Line Job Queue", default=False)
    perform_reversal_by_line_jq = fields.Boolean(string="Perform Reversal by Line Job Queue", default=False)