/** @odoo-module **/
import { registry } from "@web/core/registry";

export async function viewReload(env, action) {
     env.bus.trigger("CLEAR-CACHES");
     env.services.action.doAction('soft_reload')

}

registry.category("actions").add("view_reload", viewReload);
