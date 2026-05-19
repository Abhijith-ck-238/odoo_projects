 /** @odoo-module **/
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";
import {Dropdown} from '@web/core/dropdown/dropdown';
import {DropdownItem} from '@web/core/dropdown/dropdown_item';

class SystrayDropdown extends Component {
   setup() {
       this.action = useService("action");
   }
   _openSaleModel() {
       this.action.doAction({
           type: "ir.actions.act_window",
           name: "Sale Order",
           res_model: "sale.order",
           views: [[false, "list"], [false, "form"]],
           target: "current",
           });
           }
   _openPurchaseModel(){
       this.action.doAction({
           type: "ir.actions.act_window",
           name: "Purchase Order",
           res_model: "purchase.order",
           views: [[false, "list"], [false, "form"]],
           target: "current",
           });
    }
}
   SystrayDropdown.template = "systray_dropdown";
   SystrayDropdown.components = {Dropdown, DropdownItem };
   export const systrayItem = { Component: SystrayDropdown,};
   registry.category("systray").add("SystrayDropdown", systrayItem, { sequence: 1 });
