/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import {Dialog} from "@web/core/dialog/dialog";

export class ChatterDialog extends Component {
    static template = "cyllo_studio.ChatterDialog";
    static components = {
        Dialog,
    };
    setup() {
        this.rpc = useService('rpc');
        this.action = useService('action');
    }
    async confirm(){
        this.env.services.ui.block();
        try{
           const response =  await this.rpc("cyllo_studio/add_remove/chatter", {
               model: this.props.model,
               view_id: this.props.view_id,
               path: this.props.path,
               view_type: "form",
               position: this.props.position,
            })
            if(response){
                let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                let cleanedStr = response.replace(/\s+/g, ' ').trim();
                storedArray.push(cleanedStr)
                sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                sessionStorage.setItem('ReDO', JSON.stringify([]));
            }
        } finally {
            this.env.services.ui.unblock();
        }
         this.env.bus.trigger('restChatter')
        this.action.doAction('studio_reload')
    }
    onCancel(){
        this.action.doAction('studio_reload')
    }
}
