/** @odoo-module **/
import { registry } from "@web/core/registry";
import { calendarView } from "@web/views/calendar/calendar_view";
import { cylloCalendarRenderer } from "./cyllo_calendar_renderer";

export const cylloCalendarView = {
   ...calendarView,
   Renderer: cylloCalendarRenderer,
}
registry.category("views").add("calendar", cylloCalendarView, {force: true});
