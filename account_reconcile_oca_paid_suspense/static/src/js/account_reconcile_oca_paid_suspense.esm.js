/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AccountReconcileDataWidget } from "@account_reconcile_oca/js/widgets/reconcile_data_widget.esm";

patch(AccountReconcileDataWidget.prototype, 'account_reconcile_oca_paid_suspense', {
    async onFullyPaidSuspense(ev, reconcile_line) {
        ev.stopPropagation();
        const new_data = await this.orm.call("account.bank.statement.line", "button_fully_paid_suspense", [[this.props.record.data.id], reconcile_line.reference, this.props.record.data[this.props.name]]);
        this.props.record.update({[this.props.name]: new_data, can_reconcile: new_data.can_reconcile});
    },
});
