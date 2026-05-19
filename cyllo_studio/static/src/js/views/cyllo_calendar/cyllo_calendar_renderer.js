/** @odoo-module **/
import {
    CalendarRenderer
} from "@web/views/calendar/calendar_renderer";
import {
    CalendarController
} from "@web/views/calendar/calendar_controller";
import {
    onMounted
} from "@odoo/owl";

CalendarController.template = 'cyllo_studio.CylloCalendarController'

export class cylloCalendarRenderer extends CalendarRenderer {
    setup() {
        super.setup();
        onMounted(() => {
            this.env.bus.trigger("CALENDAR_DETAILS", {
                model: this.props.model.meta.resModel,
                viewId: this.env.config.viewId,
                viewType: this.env.config.viewType,
                mode: this.props.model.meta,
                activeFields: this.props.model.meta.activeFields,
//                model: this.props.model,
                calendar_info: this.props.model
            });
        });
    }
}
