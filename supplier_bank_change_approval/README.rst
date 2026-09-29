Supplier Bank Account Approval
==============================

1. Adds a state (draft / confirmed) to the bank accounts of a partner.
   Only applies to partners flagged with is_supplier (from partner_manual_rank);
   a bank account of any other partner (a customer, or the company itself) is
   always considered approved.
2. New menu 'Sensitive Fields Approval' where changes can be approved.
   Only visible to the new security group 'Bank Account Manager'.
3. A bank account that is added or changed goes back to draft, and a draft
   account cannot be used anywhere until it is confirmed:

   Invoices
     - Draft accounts are excluded from the Recipient Bank dropdown and are
       never proposed as the default.
     - Saving an invoice that refers to a draft account is refused.
     - Posting is refused as well, which also covers accounts that were
       approved when they were selected and were sent back to draft afterwards.

   Payments
     - Draft accounts are excluded from the Recipient Bank Account dropdown,
       both on the payment itself and in the Register Payment wizard.
     - Saving and posting a payment that refers to a draft account is refused.

   Payment orders
     - A payment line cannot hold a draft account; journal items without a bank
       account of their own fall back to the first approved account.
     - Confirming the order and generating the payment file are both refused
       while any line still refers to a draft account.

Note on installation
--------------------
The state column is added with 'draft' as its default, so every bank account
that already exists at install time becomes draft, including the supplier
accounts that were in use. Approve them in bulk from
Sensitive Fields Approval / Bank Account Approval, otherwise existing vendor
bills referring to them cannot be posted.
