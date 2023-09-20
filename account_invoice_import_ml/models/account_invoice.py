# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import json
import base64
import logging
from odoo import fields, models,_
# Import `Serialized` field straight to avoid:
from odoo.addons.base_sparse_field.models.fields import Serialized

_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    import_ml_result = Serialized('ML result')
    import_ml_warnings = fields.Html('ML warnings')

    def _account_invoice_import_ml_export(self):
        # TODO in which format do we need to export this?
        result = []
        for this in self:
            line = this.invoice_line_ids[:1]
            attachment = self.env['ir.attachment'].search([
                ('res_model', '=', this._name),
                ('res_id', '=', this.id),
                ('mimetype', '=', 'application/pdf'),
            ], order='create_date asc', limit=1)
            if not attachment:
                _logger.info('Ignoring invoice %s because no PDF attachment found', this.name or this.id)
                continue
            data = {
                "vendor_id": str(this.partner_id.id),
                "vendor_name": this.partner_id.name,
                "vat_amount": str(this.amount_tax),
                "net_amount": str(this.amount_untaxed),
                "gross_amount": str(this.amount_total),
                "invoice_date": this.date_invoice,
                "invoice_reference": this.reference,
                # TODO we ignore this on input currently
                "line_price": 0,
                "line_description": line.name,
                "account_number": line.account_id.code,
                "account_name": line.account_id.name,
                "analytic_account_code": line.account_analytic_id.code,
                "analytic_account_name": line.account_analytic_id.name,
                "pdf": attachment.datas,
            }
            if 'operating_unit_id' in self._fields:
                data["operating_unit"] = line.operating_unit_id.name
            result.append(data)
        return result
