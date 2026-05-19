/** @odoo-module */
import {registry} from "@web/core/registry";
import {CylloKanbanRenderer} from "./cyllo_kanban_renderer";
import { kanbanView } from "@web/views/kanban/kanban_view";


export const CylloKanbanView = {
    ...kanbanView,
    Renderer: CylloKanbanRenderer,
};


registry.category("views").add("kanban", CylloKanbanView, {force: true});

