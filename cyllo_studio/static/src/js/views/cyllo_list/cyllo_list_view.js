/** @odoo-module */
import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { CylloListRenderer } from "./cyllo_list_renderer";

export const CylloListView = {
  ...listView,
  Renderer: CylloListRenderer,
};

registry.category("views").add("list", CylloListView, { force: true });
