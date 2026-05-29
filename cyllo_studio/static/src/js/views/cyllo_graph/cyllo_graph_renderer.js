/** @odoo-module */
import { GraphRenderer } from "@web/views/graph/graph_renderer";
import { onMounted } from "@odoo/owl";

export class CylloGraphRenderer extends GraphRenderer {
  setup() {
    super.setup();
    console.log("yrewefdssff", this.model.updateMetaData);
    onMounted(() => {
      this.env.bus.trigger("GRAPH_DETAILS", {
        model: this.props.model.metaData.resModel,
        mode: this.props.model.metaData,
        viewType: this.env.config.viewType,
        viewId: this.env.config.viewId,
        allFields: this.props.model.metaData.fields,
        envModel:this.model,
      });
    });
  }
}
