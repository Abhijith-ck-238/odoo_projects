/** @odoo-module **/
import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class ReservationIcon extends Component {
    static template = "custom_guest_house.WidgetReservationIcon";
    static props = {
        ...standardFieldProps,
    };

}

// Register the widget in field registry
registry.category("fields").add("reservation_icon", {
    component: ReservationIcon,
});