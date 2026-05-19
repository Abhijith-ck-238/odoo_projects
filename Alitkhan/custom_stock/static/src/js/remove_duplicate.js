/** @odoo-module **/

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
console.log("hi")

class CustomListController extends ListController {
    setup() {
        super.setup();
        this.orm = useService("orm");
    }

    async removeSelectedRecords() {
        const selectedIds = await this.getSelectedResIds();

        if (!Array.isArray(selectedIds)) {
            return;
        }

        if (selectedIds.length > 0) {
            await this.orm.call(
                "stock.valuation.layer",
                "unlink_selected_inventory_valuation_entries",
                [selectedIds]
            );
            await this.model.load();
            this.model.notify();
        }
    }

}

registry.category("views").add("custom_valuation_list", {
    ...listView,
    Controller: CustomListController,
    buttonTemplate: "custom_stock.RemoveButtonTemplate",
});
