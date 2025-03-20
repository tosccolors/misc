from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _set_account_analytic_required_default_account(self):
        for this in self:
            if (
                    this.account_id._get_analytic_policy() == 'always'
                    and not this.analytic_account_id
                    and not this._has_analytic_distribution()
            ):
                default_account = this.account_id.user_type_id.with_company(
                        this.company_id
                    ).property_default_account
                if default_account:
                    this.analytic_account_id = default_account

    @api.constrains("analytic_account_id", "account_id", "debit", "credit")
    def _check_analytic_required(self):
        self._set_account_analytic_required_default_account()
        return super()._check_analytic_required()
