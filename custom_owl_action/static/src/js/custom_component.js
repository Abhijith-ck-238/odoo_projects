/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, useRef } from "@odoo/owl";
import { useExternalListener, useEffect } from "@odoo/owl";

class CustomAction extends Component {
    static template = "custom_owl_action.CustomAction";

    setup() {
        this.state = useState({
            message: "Window Size Tracker",
            width: window.innerWidth,
            height: window.innerHeight,
        });
        this.root = useRef("main_custom_section");
        useExternalListener(window, "resize", this.onWindowResized);

        useEffect(
            () => {
                this.updateBackgroundByWidth();
            },
            () => [this.state.width]
        );
    }

    updateBackgroundByWidth() {
        const el = this.root.el;
        if (!el) {
            return;
        }
        let color = "";
        if (this.state.width > 1200) {
            color = "#d4edda";   // light green
        } else if (this.state.width > 992) {
            color = "#fff3cd";   // light yellow
        } else if (this.state.width > 768) {
            color = "#ffe5b4";   // orange warning
        } else {
            color = "#f8d7da";   // light red
        }
        el.style.backgroundColor = color;
        el.style.transition = "background-color 0.4s ease";
    }

    onWindowResized() {
        this.state.width = window.innerWidth;
        this.state.height = window.innerHeight;
    }

}

registry.category("actions").add("custom_owl_action.action_js", CustomAction);
