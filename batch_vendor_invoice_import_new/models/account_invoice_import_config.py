# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields
from odoo.tools.translate import _


class account_invoice_import_config(models.Model):
    _inherit = "account.invoice.import.config"

    operating_unit_id = fields.Many2one('operating.unit',
        string=_("Operating Unit"),
        ondelete='cascade',
        default=lambda self: self.env['res.company']._company_default_get(
            'account.invoice.import.config'),
        required=False,
        translate=False,
        readonly=False
    )
