Vendor bills: Fields to flag deviations from purchase order
===========================================================

This addons adds fields ``invoice_lines_differ_po_quantity`` and ``invoice_lines_differ_po_price_unit`` on invoices.

This allows you to ie create tier validations that only trigger for invoices that either don't derive from a purchase order, or deviate from it.

Use domain::

    '|', ('invoice_lines_differ_po_quantity', '=', True), ('invoice_lines_differ_po_price_unit', '=', True)

to identify such invoices (the fields are True when there's no PO)
