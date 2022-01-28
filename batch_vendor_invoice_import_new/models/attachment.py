# -*- coding: utf-8 -*-
# Copyright 2017 Willem Hulshof ((www.magnus.nl).)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from base64 import b64decode
import hashlib
import logging
import odoo
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from unidecode import unidecode


_logger = logging.getLogger(__name__)


class IrAttachmentMetadata(models.Model):
    # _inherit = ['ir.attachment.metadata']
    _inherit = ['attachment.queue']

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        translate=False,
        readonly=True
    )
    user_id = fields.Many2one(related='task_id.user_id', relation='res.users', string='User from Task')
    parsed_invoice_text = fields.Text('Parsed Invoice Text')

    _sql_constraints = [
        ('hash_uniq', 'unique(internal_hash, location_id)',
         _('Hash of Invoice must be unique per import/export location!')),
    ]

    @api.multi
    def run(self):
        """
        Run the process for each attachment metadata
        """
        biil_recordset = self.filtered(lambda a: a.location_id == self.env.ref('batch_vendor_invoice_import_new.batch_invoice_import_location'))
        other_recordset = self - biil_recordset
        super(IrAttachmentMetadata, other_recordset).run()
        for attachment in biil_recordset:
            if attachment.task_id.user_id:
                user_id = attachment.task_id.user_id.id
            else:
                user_id = self.env.uid
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    new_env = api.Environment(
                        new_cr, user_id, self.env.context)
                    attach = attachment.with_env(new_env)
                    try:
                        attach._run()
                    except Exception as e:
                        attach.env.cr.rollback()
                        _logger.exception(e)
                        attach.write(
                            {
                                'state': 'failed',
                                'state_message': e,
                            })
                        attach.env.cr.commit()
                    else:
                        vals = {
                            'state': 'done',
                            'sync_date': fields.Datetime.now(),
                        }
                        attach.write(vals)
                        attach.env.cr.commit()
        return True

    @api.multi
    def _run(self):
        super(IrAttachmentMetadata, self)._run()
#        if self.location_id == self.env.ref('batch_vendor_invoice_import_new.batch_invoice_import_location'):
        vals = {
                'invoice_file': self.datas,
                'invoice_filename': self.name,
                'task_id': self.task_id.id,
                'company_id': self.company_id.id,
                'operating_unit_id': self.operating_unit_id.id,
        }
        self.env['account.invoice.import'].create(vals).import_invoice()
