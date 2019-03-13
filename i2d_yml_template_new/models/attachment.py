# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode
import hashlib
import logging
import odoo
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import os


_logger = logging.getLogger(__name__)


class IrAttachmentMetadata(models.Model):
    _inherit = ['ir.attachment.metadata']

    file_type = fields.Selection(
        selection_add=[
            ('delete_external_location',
             'Delete File (External location)')
        ])


    @api.multi
    def _run(self):
        super(IrAttachmentMetadata, self)._run()
        if self.file_type == 'delete_external_location':
            protocols = self.env['external.file.location']._get_classes()
            location = self.location_id
            cls = protocols.get(location.protocol)[1]
            path = os.path.join(self.task_id.filepath, self.datas_fname)
            with cls.connect(location) as conn:
                if self.file_type == 'delete_external_location':
                    conn.remove(path)
