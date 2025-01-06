# -*- coding: utf-8 -*-

from odoo import models, fields

class AccountConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # perform_posting_by_line = fields.Boolean(string="Experimental - Perform Posting by Line",
    #                                          related='company_id.perform_posting_by_line', readonly=False)
    use_description_as_reference = fields.Boolean(string="Use description as reference",
                                                  related='company_id.use_description_as_reference', readonly=False)
    perform_posting_by_line_jq = fields.Boolean(string="Perform Posting by Line Job Queue",
                                                related='company_id.perform_posting_by_line_jq', readonly=False)
