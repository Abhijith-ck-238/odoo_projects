/** @odoo-module **/

import { registry } from "@web/core/registry";
import { BlockUI } from "@web/core/ui/block_ui";
import { download } from "@web/core/network/download";


registry.category("ir.actions.report handlers").add("custom_helpdesk_xlsx", async function (action){
    if (action.report_type === "custom_helpdesk_xlsx")
    {
        BlockUI;
        await download({url:"/custom_helpdesk_xlsx",data:action.data,complete:() => unblockUI,error:(error) => self.call('crash_manager','rpc_error',error)})
    }
})
