from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_lines_differ_po_price_unit = fields.Boolean(
        compute="_compute_invoice_lines_differ_po", store=True, compute_sudo=True
    )
    invoice_lines_differ_po_quantity = fields.Boolean(
        compute="_compute_invoice_lines_differ_po", store=True, compute_sudo=True
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
        "invoice_line_ids.purchase_line_id",
        "invoice_line_ids.quantity",
        "invoice_line_ids.price_unit",
    )
    def _compute_invoice_lines_differ_po(self):
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
                this.invoice_lines_differ_po_price_unit = True
                this.invoice_lines_differ_po_quantity = True
                continue

            if invoice_lines.filtered(lambda x: not x.purchase_line_id):
                this.invoice_lines_differ_po_price_unit = True
                this.invoice_lines_differ_po_quantity = True
                continue

            if po_lines.order_id.order_line - po_lines:
                this.invoice_lines_differ_po_price_unit = True
                this.invoice_lines_differ_po_quantity = True
                continue

            this.invoice_lines_differ_po_price_unit = _comparison_dict(
                invoice_lines, "price_unit"
            ) != _comparison_dict(po_lines, "price_unit")

            this.invoice_lines_differ_po_quantity = _comparison_dict(
                invoice_lines, "quantity"
            ) != _comparison_dict(po_lines, "product_qty")
