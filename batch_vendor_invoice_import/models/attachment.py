# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode
import hashlib
import logging
import odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class IrAttachmentMetadata(models.Model):
    _inherit = ['ir.attachment.metadata']

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        translate=False,
        readonly=True
    )


    @api.multi
    def _run(self):
        super(IrAttachmentMetadata, self)._run()
        if self.location_id == self.env.ref('batch_vendor_invoice_import.batch_invoice_import_location'):
            vals = {
                'invoice_file': self.datas,
                'invoice_filename': self.name,
                'task_id': self.task_id.id,
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
            }
            self.env['account.invoice.import'].create(vals).create_invoice_action()
