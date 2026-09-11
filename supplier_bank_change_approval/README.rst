1. Add state draft and confirmed to the banks_account_ids from partner.
   This should only apply to partners is supplier = true
2. New menu called 'Sensitive fields approval' where any changes can be approved.
   This menu should only be visible and available to new security group 'Bank Account Manager'
3. When a bank account is changed or added, it will be in draft state. It cannot be used
   until it has been confirmed:

   - Invoices: only confirmed bank accounts can be selected as recipient bank, and a draft
     account is never proposed as default. Saving an invoice with a draft account is refused.
   - Payments (incl. the register payment wizard): only confirmed bank accounts can be
     selected; saving a payment with a draft account is refused.
   - Payment orders: a payment line cannot hold a draft bank account, journal items without a
     bank account fall back to the first confirmed one, and confirming / generating the
     order is refused while any line still refers to a draft account.
