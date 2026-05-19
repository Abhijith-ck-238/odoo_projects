/** @odoo-module **/
import { Component,useRef } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";

// Define the dialog component to display order lines

export class PurchaseOrderLineDialog extends Component {
    static template = "logistics.PurchaseOrderLineDialog";
    static components = { Dialog };
    static props = {
        title:String,
        resModel:String,
        close: Function,
        orderLines:Object
        };
}