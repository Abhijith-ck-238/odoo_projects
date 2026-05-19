/** @odoo-module **/
import { Component } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { StatusBarDialog } from "@cyllo_studio/js/views/cyllo_form/status_bar/statusbar_dialog";
import { useState,onMounted } from "@odoo/owl";


export class StatusBar extends Component {
    setup() {
        this.dialogService = useService("dialog");
            this.state = useState({
                isVisible: true,
            })
            onMounted(() => {
            const sheet = document.querySelector('.o_form_sheet')?.getAttribute('sheet')
            if(sheet){
                this.state.isVisible = false
            }
          })
    }
    onClick() {
        console.log("dailogterer",this)
        this.dialogService.add(StatusBarDialog,{
            fields: this.props.fields,
            path: this.props.path,
            viewId: this.props.viewId,
            model: this.props.model,
            header: this.props.header,
            activeFields: this.env.model.config.activeFields,
        })
    }
}
StatusBar.template = "cyllo_studio.StatusBar";
StatusBar.props = { fields: Object, viewId: Number, model: String, path: String, header: String }
