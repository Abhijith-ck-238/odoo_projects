/** @odoo-module **/
import { Component, onWillStart, useState, useEffect } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { RecordSelector } from "@web/core/record_selectors/record_selector";
import { Dialog } from "@web/core/dialog/dialog";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";


export class AvatarDialog extends Component {
    static template = "cyllo_studio.AvatarDialog";
    static components = {
        Dialog,
        CylloStudioDropdown
    };
    setup() {
        this.rpc = useService('rpc');
        this.action = useService('action');
        this.state = useState({
            field: "existing",
            existingFieldTech: "",
            newFieldLabel: "",
            newFieldTechName: "",
        })
    }

    get existingFields() {
        const binaryFields = Object.entries(this.props.fields)
            .filter(([key, field]) => field.type === "binary" && field.store)
            .map(([key, field]) => ({ name: field.name, string: field.string }));
        return binaryFields
    }

    onInputLabel(ev) {
        if (!this.state.newFieldTechName || this.state.newFieldTechName == this.processTechName(this.state.newFieldLabel)) {
            this.onInputTechName(ev)
        }
        this.state.newFieldLabel = ev.target.value
    }

    onInputTechName(ev) {
        let inputValue = ev.target.value;
        this.state.newFieldTechName = this.processTechName(inputValue);
    }

    processTechName(inputValue) {
        inputValue = inputValue.replace(/ /g, "_");
        inputValue = inputValue.replace(/[^a-zA-Z0-9_]/g, "");
        return inputValue.toLowerCase()
    }

    avatarExistingFields(array){
        console.log("Asdasdasdasdasdasdas")
        const result = array.map(item => ({ value: item.name, label:item.string }));
        return result
    }

    handleAvatarExistingFields(value) {
        this.state.existingFieldTech = value;
    }

    get defaultAvatarExistingField() {
        return this.state.existingFieldTech
     }

    async onConfirm() {
        if (this.state.field === 'existing') {
            if (!this.state.existingFieldTech) {
                return this.action.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Select an existing field',
                        'type': 'warning',
                        'sticky': false,
                    }
                })
            }
            this.env.services.ui.block();
            try{
               const response =  await this.rpc("cyllo_studio/add/avatar", {
                    path: this.props.path,
                    view_id: this.props.viewId,
                    is_new: false,
                    model: this.props.model,
                    view_type: "form",
                    field: {
                        name: this.state.existingFieldTech,
                        }
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
            this.action.doAction('studio_reload')
        } else {
            if (!this.state.newFieldLabel || !this.state.newFieldTechName) {
                return this.action.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Both fields are required',
                        'type': 'warning',
                        'sticky': false,
                    }
                })
            }
             this.env.services.ui.block();
            try{
                const response = await this.rpc("cyllo_studio/add/avatar", {
                    path: this.props.path,
                    view_id: this.props.viewId,
                    is_new: true,
                    model: this.props.model,
                    view_type: "form",
                    field: {
                        name: "x_cy_" + this.state.newFieldTechName,
                        label: this.state.newFieldLabel
                        }
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
            this.action.doAction('studio_reload')
        }
        this.props.close()
    }
    onDiscard() {
        this.props.close();
    }
}