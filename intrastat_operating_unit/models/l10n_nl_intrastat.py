# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ReportIntrastat(models.Model):
    _inherit = 'l10n_nl.report.intrastat'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
    )

    @api.multi
    def generate_lines(self):
        """
        Collect the data lines for the given report.
        Unlink any existing lines first.
        """
        self.ensure_one()

        # Other models:
        Invoice = self.env['account.invoice']
        InvoiceLine = self.env['account.invoice.line']

        # Check whether all configuration done to generate report
        self._check_generate_lines()

        # Define search for invoices for period and company:
        company = self.company_id
        invoice_domain = [
            ('type', 'in', ('out_invoice', 'out_refund')),
            ('date_invoice', '>=', self.date_from),
            ('date_invoice', '<=', self.date_to),
            ('state', 'in', ('open', 'paid')),
            ('company_id', '=', company.id),
        ]

        # Search invoices that need intracom reporting:
        company_country = company.country_id
        invoice_domain += [
            ('commercial_partner_id.country_id.intrastat', '=', True),
            ('commercial_partner_id.country_id.id', '!=', company_country.id),
        ]
        if self.operating_unit_id:
            invoice_domain += [
                ('operating_unit_id', '=', self.operating_unit_id.id),
            ]
        invoice_records = Invoice.search(invoice_domain)

        invoice_line_domain = [('invoice_id', 'in', invoice_records.ids)]
        if self.operating_unit_id:
            invoice_line_domain += [
                ('operating_unit_id', '=', self.operating_unit_id.id),
            ]
        invoice_line_records = InvoiceLine.search(invoice_line_domain)

        # Gather amounts from invoice lines
        total_amount = 0.0
        partner_amounts_map = {}
        for line in invoice_line_records:
            # Ignore invoiceline if taxes should not be included:
            if any(
                    tax.exclude_from_intrastat_if_present
                    for tax in line.invoice_line_tax_ids):
                continue
            # Report is per commercial partner:
            commercial_partner = line.invoice_id.commercial_partner_id
            amounts = partner_amounts_map.setdefault(commercial_partner, {
                'amount_product': 0.0,
                'amount_service': 0.0,
            })
            # Determine product or service, don't look at is_accessory_cost
            if line.product_id.type == 'service':
                amount_type = 'amount_service'
            else:
                amount_type = 'amount_product'
            sign = line.invoice_id.type == 'out_refund' and -1 or 1
            amount = sign * line.price_subtotal
            # Convert currency amount if necessary:
            currency = line.invoice_id.currency_id
            invoice_date = line.invoice_id.date_invoice
            if (currency and currency != company.currency_id):
                amount = currency.with_context(date=invoice_date).compute(
                    amount, company.currency_id, round=True)
            # Accumulate totals:
            amounts[amount_type] += amount  # per partner and type
            total_amount += amount  # grand total

        # Determine new report lines
        new_lines = []
        for (partner, vals) in partner_amounts_map.iteritems():
            if not (vals['amount_service'] or vals['amount_product']):
                continue
            vals.update({'partner_id': partner.id})
            new_lines.append(vals)

        # Set values and replace existing lines by new lines
        self.line_ids.unlink()
        self.write({
            'last_updated': fields.Datetime.now(),
            'line_ids': [(0, False, line) for line in new_lines],
            'total_amount': total_amount
        })