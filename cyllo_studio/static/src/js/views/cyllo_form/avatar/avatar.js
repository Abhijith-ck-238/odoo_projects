/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { AvatarDialog } from "@cyllo_studio/js/views/cyllo_form/avatar_dailog/avatar_dialog";
import { useState,onMounted } from "@odoo/owl";

export class AvatarComponent extends Component {
    setup() {
        console.log("asdasdasdqwdqwqwdqwd",this)
        this.dialogService = useService("dialog");
        this.state = useState({
            isVisible : true,
        });
        onMounted(() => {
            const sheet = document.querySelector('.o_form_sheet')?.getAttribute('sheet')
            if(sheet){
                this.state.isVisible = false
            }
        })
    }
    onClick() {
        this.dialogService.add(AvatarDialog,{
            fields: this.props.fields,
            path: this.props.path,
            viewId: this.props.viewId,
            model: this.props.model
        })
    }
}
AvatarComponent.template = "cyllo_studio.AvatarComponent";
AvatarComponent.props = { fields: Object, viewId: Number, model: String, path: String }
