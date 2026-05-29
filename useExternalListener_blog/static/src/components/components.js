import { Component, useExternalListener } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService} from "@web/core/utils/hooks";

console.log('aaaaaaaaaaaaaaaaaa')
export class CustomComponent extends Component {
    static template = "useExternalListener_blog.CustomComponent";

    setup() {
        this.action = useService("action")
        useExternalListener(window, "keypress", this.onKeyPress, true);
    }

    onKeyPress(){
        this.action.doAction({
            type: "ir.actions.client",
            tag: "display_notification",
            params: {
                message: "Keyboard events triggered",
                sticky: false,
            },
        });
    }
}

registry.category("actions").add("custom_client_action.main", CustomComponent);
