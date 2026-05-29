/** @odoo-module **/
import { registry } from "@web/core/registry";

async function studioReload(env, action) {
     env.bus.trigger("CLEAR-CACHES");
     env.services.action.doAction('soft_reload')

}

registry.category("actions").add("studio_reload", studioReload);
