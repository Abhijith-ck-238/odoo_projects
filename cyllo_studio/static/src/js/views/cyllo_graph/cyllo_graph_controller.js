/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { GraphController } from "@web/views/graph/graph_controller";
import { useService } from "@web/core/utils/hooks";
import { useRef, onMounted } from "@odoo/owl";
import { Layout } from "@web/search/layout";

patch(GraphController.prototype, {
    setup() {
        super.setup();
        console.log("ddddddddddddddddddddddddd")
        this.rpc = useService('rpc')
        this.action = useService('action')
        onMounted(async () => {
            console.log('%c Onmounted Graph controller', 'color: white; background-color: red; padding: 2px; border-radius: 3px;',this,this.env.config);
            if (!this.env.config.viewId) {
                await this.createGraphView()
            }
            this.env.bus.trigger('graphDetails', {
                view_type: this.env.config.viewType,
                model: this.model.env.searchModel.resModel,
                envModel: this,
                active_fields: this.props.fields,
                measure: this.model.metaData.measure,
            });
        })
    },

    async createGraphView() {
        console.log('%c CreateGraphview', 'color: white; background-color: red; padding: 2px; border-radius: 3px;',this.env.config.viewArch.outerHTML,this.props.resModel);

        this.env.services.ui.block();
        try {
            await this.rpc("cyllo_studio/graph/add_view", {
                arch: this.env.config.viewArch.outerHTML,
                model: this.props.resModel,
            })
        } finally {
            this.env.services.ui.unblock();
        }
        this.action.doAction("studio_reload");

    }
})

GraphController.components = {
    ...GraphController.components,
    Layout,
}
GraphController.template = "studio.CylloGraphView"
