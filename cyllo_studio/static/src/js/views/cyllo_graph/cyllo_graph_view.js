/** @odoo-module */
import { registry } from "@web/core/registry";
import { graphView } from "@web/views/graph/graph_view";
import { CylloGraphRenderer } from "./cyllo_graph_renderer";

export const CylloGraphView = {
  ...graphView,
  Renderer: CylloGraphRenderer,
};

registry.category("views").add("graph", CylloGraphView, { force: true });
