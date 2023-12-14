/** @odoo-module */

import { ListController } from "@web/views/list/list_controller";
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";

export class MontaStockListController extends ListController {
    onClickMontaStockLot() {
        this.actionService.doAction({
            res_model: "monta.product.stock.wizard",
            views: [[false, "form"]],
            target: "new",
            type: "ir.actions.act_window",
        });
    }
}
registry.category("views").add('monta_product_stock_lot_list', {
    ...listView,
    Controller: MontaStockListController,
    buttonTemplate: 'MontaStockLot.Buttons',
});

