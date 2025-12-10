# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Magnus NL (<http://magnus.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class Invoice(models.Model):
    """ Inherits invoice and adds ad boolean to invoice to flag Advertising-invoices"""
    _inherit = 'account.move'

    has_failed2confirm = fields.Boolean('Failed to auto-validate', default=False, copy=False)



    def _do_invoice_sent_wizard(self):
        self.ensure_one()
        wiz_send_invoice = self.env['account.invoice.send']
        ctx = dict(self.env.context)

        if self.is_move_sent:
            return _("This invoice has already been sent.")

        res = self.action_invoice_sent()
        ctx = res["context"] or {}
        ctx["active_model"] = self._name
        ctx["active_ids"] = self.ids

        wsi_vals = wiz_send_invoice.with_context(ctx).default_get(['template_id', 'partner_ids'])
        wiz = self.env["account.invoice.send"].with_context(**ctx).create(wsi_vals)
        wiz.write({
            "is_print": False,
            "is_email": True,
            'auto_delete': False,
            "composition_mode": "mass_mail",
        })
        return wiz.send_and_print_action()


    def _cron_auto_validate_invoices(self):
        "Called from Cron, to validate Out-Invoices which are in draft status."

        draftInvoices = self.search([('move_type', '=', 'out_invoice'), ('state', 'in', ('draft', 'sent'))], order='id, invoice_date')

        for invoice in draftInvoices:
            try:
                invoice.action_post()
                invoice.has_failed2confirm = False
                invoice.message_post(body=_(
                    'This invoice has been auto validated.'))

                # Send Email: Check Amount & Transmission Method
                if invoice.amount_total > 0 and invoice.transmit_method_id.id != self.env.ref('auto_validate_invoice.no_send_mail').id:
                    invoice._do_invoice_sent_wizard()

            except Exception as e:
                invoice.has_failed2confirm = True
                invoice.message_post(body=_(
                    'Unable to auto validate this invoice;  %s.')
                                 % (str(e)))