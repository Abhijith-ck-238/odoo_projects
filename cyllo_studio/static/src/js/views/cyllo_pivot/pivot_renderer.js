/** @odoo-module **/
import {
    useRef,
    onPatched,
    onMounted,
    useState
} from "@odoo/owl";
import {
    PivotRenderer
} from "@web/views/pivot/pivot_renderer";

export class CylloPivotRenderer extends PivotRenderer {
    setup() {
        super.setup();
        onMounted(() => {
            this.env.bus.trigger("PIVOT_DETAILS", {
                viewType: this.env.config.viewType,
                viewId: this.env.config.viewId,
                envModel: this,
                model: this.props.model.metaData.resModel,
                active_fields: this.props.model.metaData.fields,
                measure: this.model.metaData.measures,
                metaData: this.model.metaData,
                activeFields: this.model.metaData.fields,
            });
        });
    }
}
CylloPivotRenderer.template = "cyllo_studio.StudioPivotRenderer"
CylloPivotRenderer.components = {
    ...PivotRenderer.components,
};