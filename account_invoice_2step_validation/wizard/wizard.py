# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Eurogroup Consulting BV (www.eurogroupconsulting.nl).
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

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountInvoiceConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft/start_wf invoices
    """

    _inherit = "account.invoice.confirm"
    _description = "Confirm the selected invoices"

    @api.multi
    def invoice_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if (record.type in ('in_invoice', 'in_refund') and record.state != 'start_wf') or \
                    (record.type in ('out_invoice', 'out_refund') and record.state not in ('draft', 'proforma', 'proforma2')):
                raise UserError(_("Selected invoice(s) cannot be confirmed as they are not in 'Start Workflow' (Vendor Invoices), 'Draft' or 'Pro-Forma' (Customer Invoices) state."))
            record.action_invoice_open()
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceStartWf(models.TransientModel):
    """
    This wizard will set all the selected draft invoices to start_wf
    """

    _name = "account.invoice.startwf"
    _description = "Start Workflow of the selected invoices"

    @api.multi
    def invoice_startwf(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.type not in ('in_invoice', 'in_refund') or record.state != 'draft':
                raise UserError(_("Selected invoice(s) cannot be started as they are not in 'Draft' state or they are Customer invoices."))
            record.action_invoice_start_wf()
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceAuthor(models.TransientModel):
    """
    This wizard will authorize  all the selected open invoices for payment
    """

    _name = "account.invoice.author"
    _description = "Authorize the selected invoices"

    @api.multi
    def invoice_author(self):
        context = dict(self._context)
        InvObj = self.env['account.invoice']

        for inv in InvObj.browse(context.get('active_ids',[])):
            # -- deep: Allow Supplier Invoice only
            if inv.type != 'in_invoice': continue

            if inv.state != 'open':
                raise UserError(_("Selected invoice(s) cannot be authorized as they are not in 'Open' state."))
            inv.action_invoice_auth()

        return {'type': 'ir.actions.act_window_close'}


class AccountInvoiceVerifier(models.TransientModel):
    """
    This wizard will verify all the selected authorized invoices for payment
    """

    _name = "account.invoice.verifier"
    _description = "Verify the selected invoices"


    @api.multi
    def invoice_verifier(self):
        context = dict(self._context)
        InvObj = self.env['account.invoice']

        for inv in InvObj.browse(context.get('active_ids',[])):
            # -- deep: Allow Supplier Invoice only
            if inv.type != 'in_invoice': continue

            if inv.state != 'auth':
                raise UserError(_("Selected invoice(s) cannot be verified as they are not in 'Authorized' state."))

            # -- deep: Additional Validation,
            # triggering Verification only for those records having exceeded threshold amount
            if inv.verif_tresh_exceeded:
                inv.action_invoice_verify()

        return {'type': 'ir.actions.act_window_close'}



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
