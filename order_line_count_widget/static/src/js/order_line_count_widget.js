/** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Component } from "@odoo/owl";

export class orderLineCountPopover extends Component {
    setup() {
        this.actionService = useService("action");
    }
}
orderLineCountPopover.template = "order_line_count_widget.OrderLineCountPopOver";

export class orderLineCountWidget extends Component {
    setup() {
        this.popover = usePopover(this.constructor.components.Popover, { position: "top" });
        this.calcData = {};
    }
    showPopup(ev) {
        this.popover.open(ev.currentTarget, {
            record: this.props.record,
            calcData: this.calcData,
        });
    }
}
orderLineCountWidget.components = { Popover: orderLineCountPopover };
orderLineCountWidget.template = "order_line_count_widget.orderLineCount";

export const OrderLineCountWidget = {
    component: orderLineCountWidget,
};
registry.category("view_widgets").add("order_line_count_widget", OrderLineCountWidget);
