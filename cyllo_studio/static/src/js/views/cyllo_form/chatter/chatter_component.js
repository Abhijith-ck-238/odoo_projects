/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { Component, useState, onMounted } from "@odoo/owl";

export class ChatterComponent extends Component {
    setup() {
        this.rpc = useService('rpc');
        this.action = useService('action');
    }

    async onClick() {
        this.env.services.ui.block();
        try{
            const position =  "inside"
            await this.rpc("cyllo_studio/add_remove/chatter", {
               model: this.props.model,
               view_id: this.props.viewId,
               path: this.props.path,
               view_type: "form",
               position
            })
        } finally {
            this.env.services.ui.unblock();
        }
        this.action.doAction('studio_reload')
    }
}
ChatterComponent.template = "cyllo_studio.ChatterComponent";
ChatterComponent.defaultProps = {
    path: "/form",
}
