/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { Select } from "@web/core/tree_editor/tree_editor_components";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";



export class CalendarDialog extends Component {
    static template = "cyllo_studio.CalendarDialog";
    static components = {
        Dialog,
        Select,
        CylloStudioDropdown,
        Dropdown,
        DropdownItem
    };
    setup() {
        console.log("CalendarDialog", this)
        this.action = useService('action');
        this.rpc = useService('rpc');
        this.state = useState({
            startDateField: {
                key: false,
                value: "Select an option",
            },
            stopDateField: {
                key: false,
                value: "Select an option",
            },
        })
    }

    get getOptions() {
        console.log("GetOptns", this)
        const dateFields = [];
        for (const [name, field] of Object.entries(this.props.fields)) {
            if (['date', 'datetime'].includes(field.type)) {
                dateFields.push([name, field.string]);
            }
        }

        if (dateFields.length > 0) {
//            this.state.startDateField = dateFields[0][0];
//            this.state.stopDateField = dateFields[0][0];
        } else {
           return this.action.doAction({
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Unable to add calendar view. This action is not permitted',
                    'type': 'warning',
                    'sticky': false,
          }
          })
        }

        return [...dateFields];
    }

    updateDateField(type, value) {
        const fieldMap = {
            start: "startDateField",
            stop: "stopDateField"
        };
        console.log(type,value,'aaaaaaaaaaaa',fieldMap,fieldMap[type])
        if (fieldMap[type]) {
            this.state[fieldMap[type]].key = value[0];
            this.state[fieldMap[type]].value = value[1];
        }
    }

    async onConfirm() {
        console.log("OnCnfirm", this)
        await this.rpc("/cyllo_studio/view/active_views", {
            args: [{
                'activeView': this.props.details[0].activeView,
                'actionId': this.props.details[0].actionId,
                'actionType': this.props.details[0].actionType,
                'viewType': this.props.details[0].viewType,
                'resModel': this.props.details[0].resModel,
                'name': this.props.details[0].name,
                'startDateField': this.state.startDateField.key,
                'stopDateField': this.state.stopDateField.key,
            }],
        });
         this.props.close();
         this.action.doAction('studio_reload')
         window.location.reload()
    }

    onDiscard() {
        this.props.close();
    }
}
