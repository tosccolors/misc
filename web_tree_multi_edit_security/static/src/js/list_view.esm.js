/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";


patch(listView, "web_tree_multi_edit_security", {
    props: function () {
        const result = this._super(...arguments);
        if (result.archInfo) {
            result.archInfo.multiEdit &&= session.has_multi_edit_security_group;
        }
        return result;
    }
});

patch(ListController.prototype, "web_tree_multi_edit_security", {
    setup: function() {
        const result = this._super(...arguments);
        this.multiEdit &&= session.has_multi_edit_security_group;
        return result;
    }
});
