# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    perform_posting_by_line = fields.Boolean(string="Experimental - Perform Posting by Line", related='company_id.perform_posting_by_line')
    use_description_as_reference = fields.Boolean(string="Use description as reference", related='company_id.use_description_as_reference')
    reversal_via_sql = fields.Boolean(string="Experimental - Reversal Via Sql", related='company_id.reversal_via_sql')
    perform_posting_by_line_jq = fields.Boolean(string="Perform Posting by Line Job Queue", related='company_id.perform_posting_by_line_jq')
    perform_reversal_by_line_jq = fields.Boolean(string="Perform Reversal by Line Job Queue", related='company_id.perform_reversal_by_line_jq')