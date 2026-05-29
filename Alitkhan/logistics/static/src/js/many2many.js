/** @odoo-module **/

import { Many2ManyTagsField } from "@web/views/fields/many2many_tags/many2many_tags_field";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component,useRef } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { rpc } from "@web/core/network/rpc";
import { PurchaseOrderLineDialog } from "./purchase_order_popup";

export class ClickableMany2ManyTags extends Many2ManyTagsField {
    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
//        this.many2ManyTagsField = useRef("many2ManyTagsField");
    }

       getTagProps(record) {
        const props = super.getTagProps(record);
        props.onClick = (ev) => this.onTagClick(ev, record);
        return props;
    }

    async onTagClick(ev, record) {
        const orderLines = await this.orm.searchRead("purchase.order.line",[["order_id", "=", record.evalContext.id]],[])
        this.dialogService.add(PurchaseOrderLineDialog,{
            title: ('Purchase Order'),
            resModel: 'purchase.order.line',
            orderLines:orderLines,
            })
    }
}


// Register the field as a Many2Many field
export const ClickableMany2Many = {
    component: ClickableMany2ManyTags,
    supportedTypes: ["many2many"],
};

registry.category("fields").add("ClickableMany2ManyTags", ClickableMany2Many);
