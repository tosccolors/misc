import math

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_lines_differ_po_price_unit = fields.Boolean(
        string="Has Price Difference With Origin PO",
        compute="_compute_invoice_lines_differ_po",
        store=True,
        compute_sudo=True,
    )
    invoice_lines_differ_po_price_unit_percentage = fields.Float(
        string="Price Difference Percentage With Origin PO",
        compute="_compute_invoice_lines_differ_po",
        store=True,
        compute_sudo=True,
    )
    invoice_lines_differ_po_quantity = fields.Boolean(
        string="Has Quantity Difference With Origin PO",
        compute="_compute_invoice_lines_differ_po",
        store=True,
        compute_sudo=True,
    )
    invoice_lines_differ_po_quantity_percentage = fields.Float(
        string="Quantity Difference Percentage With Origin PO",
        compute="_compute_invoice_lines_differ_po",
        store=True,
        compute_sudo=True,
    )

    def write(self, vals):
        # drop writes to invoice_lines_differ_po* to make the fields reliable
        drop_fields = {
            "invoice_lines_differ_po_price_unit",
            "invoice_lines_differ_po_quantity",
        }

        if drop_fields & set(vals):
            vals = {key: value for key, value in vals.items() if key not in drop_fields}

        return super().write(vals)

    @api.depends(
        "invoice_line_ids.purchase_line_id.price_unit",
        "invoice_line_ids.purchase_line_id.product_qty",
        "invoice_line_ids.quantity",
        "invoice_line_ids.price_unit",
    )
    def _compute_invoice_lines_differ_po(self):
        trivial_difference = dict(
            invoice_lines_differ_po_price_unit=True,
            invoice_lines_differ_po_quantity=True,
            invoice_lines_differ_po_price_unit_percentage=100,
            invoice_lines_differ_po_quantity_percentage=100,
        )
        for this in self:
            def _comparison_dict(lines, field_name):
                return {line.product_id.id: line[field_name] for line in lines}

            invoice_lines = this.invoice_line_ids.filtered(
                lambda x: not x.display_type
            )
            po_lines = this.invoice_line_ids.purchase_line_id.filtered(
                lambda x: not x.display_type
            )

            if not po_lines:
                this.update(trivial_difference)
                continue

            if invoice_lines.filtered(lambda x: not x.purchase_line_id):
                this.update(trivial_difference)
                continue

            if po_lines.order_id.order_line - po_lines:
                this.update(trivial_difference)
                continue

            po_price_unit_percentage = 0.0
            po_quantity_percentage = 0.0

            for line in invoice_lines:
                po_price_unit_percentage += abs(
                    1 - line.price_unit / (line.purchase_line_id.price_unit or math.inf)
                )
                po_quantity_percentage += abs(
                    1 - line.quantity / (line.purchase_line_id.product_qty or math.inf)
                )

            this.update(
                dict(
                    invoice_lines_differ_po_price_unit=po_price_unit_percentage != 0,
                    invoice_lines_differ_po_quantity=po_quantity_percentage != 0,
                    invoice_lines_differ_po_price_unit_percentage=po_price_unit_percentage
                    * 100,
                    invoice_lines_differ_po_quantity_percentage=po_quantity_percentage
                    * 100,
                )
            )
