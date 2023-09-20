# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Eurogroup Consulting NL (<http://eurogroupconsulting.nl>).
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


# added by -- deep
class Move(models.Model):
    _inherit = ['account.move']

    #
    @api.depends('amount_untaxed', 'company_id.verify_setting')
    def _compute_amount_tresh(self):
        # -- Sushma,
        #Note: removed from _compute_amount, and Added new method _compute_amount_tresh
        # Functionality for updating "verif_tresh_exceeded" are split b/w Company & Invoice Objects
        if self.company_id.verify_setting < self.amount_untaxed:
            self.verif_tresh_exceeded = True
        else:
            self.verif_tresh_exceeded = False

    name = fields.Char(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    invoice_origin = fields.Char(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    ref = fields.Char(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    # reference_type = fields.Selection(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    # comment = fields.Text(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    state = fields.Selection([
        ('draft', 'Draft'),
        ('start_wf', 'Start Workflow'),
        ('proforma', 'Pro-forma'),
        ('proforma2', 'Pro-forma'),
        ('posted', 'Posted'),
        ('auth', 'Authorized'),
        ('verified', 'Verified'),
        # ('paid', 'Paid'),
        ('cancel', 'Cancelled'),
    ], 'Status', index=True, readonly=True, track_visibility='onchange',
        help=' * The \'Draft\' status is used when a user is encoding a new and unconfirmed Invoice. \
        \n* The \'Start Workflow\' when invoice is in Start Workflow status, invoice can be adapted by first validator and validated. \
        \n* The \'Pro-forma\' when invoice is in Pro-forma status,invoice does not have an invoice number. \
        \n* The \'Authorized\' status is used when invoice is already posted, but not yet confirmed for payment. \
        \n* The \'Verified\' status is used when invoice is already authorized, but not yet confirmed for payment, because it is of higher value than Company Verification treshold. \
        \n* The \'Open\' status is used when user create invoice,a invoice number is generated.Its in open status till user does not pay invoice. \
        \n* The \'Paid\' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled. \
        \n* The \'Cancelled\' status is used when user cancel invoice.')
    invoice_date=fields.Date(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    invoice_date_due=fields.Date(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    partner_id=fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    invoice_payment_term_id=fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    date=fields.Date(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    account_id=fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    line_ids = fields.One2many(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    # tax_line_ids = fields.One2many(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    currency_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    journal_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    company_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    partner_bank_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    invoice_user_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)],'open':[('readonly',False)]})
    fiscal_position_id = fields.Many2one(states={'draft':[('readonly',False)],'start_wf':[('readonly',False)]})
    verif_tresh_exceeded = fields.Boolean(string='Verification Treshold',
                                          store=True, readonly=True, compute='_compute_amount_tresh',
                                          track_visibility='always', copy=False)
    supplier_invoice_number = fields.Char(states={'draft': [('readonly', False)], 'start_wf': [('readonly', False)]})
    payment_mode_id = fields.Many2one(states={'draft': [('readonly', False)], 'start_wf': [('readonly', False)]})

    ## Necessary??
#    payment_term = fields.Many2one('account.payment.term', 'Payment Terms',readonly=True, states={'draft':[('readonly',False)]},
#        help="If you use payment terms, the due date will be computed automatically at the generation "\
#            "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "\
#            "The payment term may compute several due dates, for example 50% now, 50% in one month.",)# groups="account.group_account_invoice")
#    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True, track_visibility='onchange', states={'draft':[('readonly',False)],'open':[('readonly',False)]})
#    reference = fields.Char('Invoice Reference', size=64, help="The partner reference of this invoice.",)# groups="account.group_account_invoice")

    # TODO: FIXME
    # amount_to_pay = fields.related('residual',
    #     type='float', string='Amount to be paid',
    #     help='The amount which should be paid at the current date.',)# groups="account.group_account_invoice")



    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(Move, self)._onchange_partner_id()
        if self.move_type in ('in_invoice', 'in_refund'):
            self.user_id = self.partner_id.vendor_owner.id
        return res

    
    # def action_date_assign(self):
    #     for inv in self:
    #         if not inv.date_due:
    #             inv._onchange_payment_term_date_invoice()
    #     return True


    # @sushma: super method not found
    # def _write(self, vals):
    #     pre_not_reconciled = self.filtered(lambda invoice: not invoice.reconciled)
    #     pre_reconciled = self - pre_not_reconciled
    #     res = super(Invoice, self)._write(vals)
    #     reconciled = self.filtered(lambda invoice: invoice.reconciled)
    #     not_reconciled = self - reconciled
    #     (reconciled & pre_reconciled).filtered(lambda invoice: invoice.state in ['auth','verified'] and
    #                                                            invoice.move_type in ['in_invoice','in_refund']).action_invoice_paid()
    #     (not_reconciled & pre_not_reconciled).filtered(lambda invoice: invoice.state == 'paid').action_invoice_re_open()
    #     return res

    # Overridden:
    def action_invoice_paid(self):
        res = super(Move, self).action_invoice_paid()
        # @sushma: check payment state instead move state
        to_pay_invoices = self.filtered(lambda inv: move.payment_state != 'paid')
        if to_pay_invoices.filtered(lambda inv: move.state not in ['auth','verified'] and
                                                               inv.move_type in ['in_invoice','in_refund']):
            raise UserError(_('Invoice must be authorized and/or verified in order to set it to register payment.'))
        # @sushma : 2 checks need to discuss then we can uncomment
        # if to_pay_invoices.filtered(lambda inv: inv.state not in ['open'] and
        #                                                        inv.move_type in ['out_invoice','out_refund']):
        #     raise UserError(_('Invoice must be open in order to set it to register payment.'))
        # if to_pay_invoices.filtered(lambda inv: not inv.reconciled):
        #     raise UserError(
        #         _('You cannot pay an invoice which is partially paid. You need to reconcile payment entries first.'))
        return res

    # @sushma methods removed
    # def action_invoice_open(self):
    #     # lots of duplicate calls to action_invoice_open, so we remove those already open
    #     to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
    #     if to_open_invoices.filtered(lambda inv: (inv.move_type in ('in_invoice', 'in_refund') and inv.state != 'start_wf') or \
    #                 (inv.move_type in ('out_invoice', 'out_refund') and inv.state not in ('draft', 'proforma', 'proforma2'))):
    #         raise UserError(_("Invoice must be in Start Workflow in the case of a Vendor Invoice or "
    #                           "Draft/Pro-forma state in the case of a Customer Invoice in order to validate it."))
    #     to_open_invoices.action_date_assign()
    #     to_open_invoices.action_move_create()
    #     return to_open_invoices.invoice_validate()


    # instead action_invoice_open used action_post
    def action_post(self):
        to_open_invoices = self.filtered(lambda inv: inv.state != 'posted')
        if to_open_invoices.filtered(
                lambda inv: (inv.move_type in ('in_invoice', 'in_refund') and inv.state != 'start_wf') or \
                                (inv.move_type in ('out_invoice', 'out_refund') and inv.state not in ('draft', 'proforma', 'proforma2'))):
                raise UserError(_("Invoice must be in Start Workflow in the case of a Vendor Invoice or "
                                  "Draft/Pro-forma state in the case of a Customer Invoice in order to validate it."))
        return super(Move, self).action_post()


    
    def action_invoice_start_wf(self):
        self.write({'state': 'start_wf'})

    
    def action_invoice_auth(self):
        self.write({'state':'auth'})

    
    def action_unauthorize(self):
        self.write({'state':'draft'})

    
    def action_invoice_verify(self):
        self.write({'state':'verified'})

    def action_unverify(self):
        return self.action_invoice_auth()

    #Overridden:
    def action_invoice_cancel(self):
        if self.filtered(lambda inv: inv.state not in ['proforma2', 'start_wf', 'draft', 'auth']):
            raise UserError(_("Invoice must be in draft, Start Workflow, Pro-forma, or Authorized state in order to be cancelled."))
        return self.action_cancel()

    #Overridden:
    def create_account_payment_line(self):
        apoo = self.env['account.payment.order']
        aplo = self.env['account.payment.line']
        result_payorder_ids = []
        action_payment_type = 'debit'
        for inv in self:
            if inv.move_type in ['in_invoice','in_refund'] and inv.state != 'verified' and not (inv.state == 'auth' and inv.verif_tresh_exceeded == False):
                raise UserError(_(
                    "The Supplier invoice %s is not in auth or verified state") % inv.number)
            if inv.move_type in ['out_invoice','out_refund'] and inv.state in ('posted', 'cancel'):
                raise UserError(_(
                    "The Customer invoice %s is not in posted state") % inv.number)
            if not inv.payment_mode_id:
                raise UserError(_(
                    "No Payment Mode on invoice %s") % inv.number)
            ##################NA##############
            # if not inv.move_id:
            #     raise UserError(_(
            #         "No Journal Entry on invoice %s") % inv.number)
            ###############################
            if not inv.payment_order_ok:
                raise UserError(_(
                    "The invoice %s has a payment mode '%s' "
                    "which is not selectable in payment orders."))
            payorders = apoo.search([
                ('payment_mode_id', '=', inv.payment_mode_id.id),
                ('state', '=', 'draft')])
            if payorders:
                payorder = payorders[0]
                new_payorder = False
            else:
                payorder = apoo.create(inv._prepare_new_payment_order())
                new_payorder = True
            result_payorder_ids.append(payorder.id)
            action_payment_type = payorder.payment_type
            count = 0
            for line in inv.move_id.line_ids:
                if line.account_id == inv.account_id and not line.reconciled:
                    paylines = aplo.search([
                        ('move_line_id', '=', line.id),
                        ('state', '!=', 'cancel')])
                    if not paylines:
                        line.create_payment_line_from_move_line(payorder)
                        count += 1
            if count:
                if new_payorder:
                    inv.message_post(_(
                        '%d payment lines added to the new draft payment '
                        'order %s which has been automatically created.')
                        % (count, payorder.name))
                else:
                    inv.message_post(_(
                        '%d payment lines added to the existing draft '
                        'payment order %s.')
                                     % (count, payorder.name))
            else:
                raise UserError(_(
                    'No Payment Line created for invoice %s because '
                    'it already exists or because this invoice is '
                    'already paid.') % inv.number)
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account_payment_order',
            'account_payment_order_%s_action' % action_payment_type)
        if len(result_payorder_ids) == 1:
            action.update({
                'view_mode': 'form,tree,pivot,graph',
                'res_id': payorder.id,
                'views': False,
            })
        else:
            action.update({
                'view_mode': 'tree,form,pivot,graph',
                'domain': "[('id', 'in', %s)]" % result_payorder_ids,
                'views': False,
            })
        return action


