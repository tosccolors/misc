# Copyright 2021 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.context.get(
                'account_invoice_import_ml_vendor_mail'
        ) and not domain and fields == ['invoice_import_email']:
            # pretend there's a company with the mail's to header to catch all mails
            return [{
                'id': self.env.user.company_id.id,
                'invoice_import_email': self.env.context.get(
                    'account_invoice_import_ml_vendor_mail',
                ),
            }]
        return super(ResCompany, self).search_read(
            domain=domain, fields=fields, offset=offset, limit=limit, order=order,
        )
