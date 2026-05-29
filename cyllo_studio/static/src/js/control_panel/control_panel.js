/** @odoo-module **/
import { ControlPanel } from "@web/search/control_panel/control_panel";
import { patch } from '@web/core/utils/patch';
import { useService } from "@web/core/utils/hooks";
import {registry} from "@web/core/registry";
import { onMounted, onWillUnmount, useState } from "@odoo/owl";

patch(ControlPanel.prototype, {
    setup(){
        super.setup()
        onMounted(() => {
            if(this.env?.config.views){
                this.env.bus.trigger("ACTIVE-VIEWS", {
                    views: this.env.config.views
                 });
            }
        })

    }
})
ControlPanel.template = "studio.CylloControlPanel"
