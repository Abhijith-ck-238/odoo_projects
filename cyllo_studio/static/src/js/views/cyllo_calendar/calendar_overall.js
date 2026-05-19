/** @odoo-module **/
import { Component, useState, onWillUpdateProps } from "@odoo/owl";
import { sortBy } from "@web/core/utils/arrays";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import { MultiSelectDropDown } from "@cyllo_studio/js/view_editor/dropdown/multi_select_dropdown/multi_select_dropdown";
import { useService } from "@web/core/utils/hooks";
import { CalendarViewDialog } from "@cyllo_studio/js/views/cyllo_calendar/calendar_field_node_dialog/calendar_field_nodes_dialog";
import { DisplayNotification } from "@cyllo_studio/js/utils/display_notification";
import { CylloRecordSelector } from "@cyllo_studio/js/view_editor/dropdown/record_selector/record_selector";
console.log("DsplyNtfctn", DisplayNotification)
export class CalendarOverall extends Component {
    static template = "cyllo_studio.CalendarOverall";
    setup() {
        this.action = useService("action");
        this.notification = useService('effect')
        this.rpc = useService("rpc");
        this.dialogService = useService("dialog");
        this.state = useState({
            ...this.state,
            openCalendar: false,
            showInvisible: false,
            calendar_info: this.props.model
        })
        onWillUpdateProps((nextProps) => {
            console.log("OnwllUpdtPrps", nextProps)
            console.log("OnwllUpdtPrps", Object.keys(nextProps.model.popoverFieldNodes))
            this.state.calendar_info = nextProps.model
            if (this.state.openCalendar) {
                this.openDialog();
            }
        })
        console.log("ClndrOvrAll", this)
    }
    openDialog() {
        console.log("OpenDialog", this)
        this.state.openCalendar = true
        if (Object.values(this.props.model.records).length) {
            this.dialogService.add(CalendarViewDialog, {
                record: Object.values(this.props.model.records)[0] || {},
                model: this.state.calendar_info,
                viewId: this.props.viewId,
                invisible: this.state.showInvisible,
                showInvisible: (invisible)=>this.invisible(invisible),
                close: () => {
                    console.log("OpenDialog11", this)
                    this.state.openCalendar = false
                    console.log("OpenDialog22", this)
                },
            })
        } else {
            return DisplayNotification(this, {
                message: "No Calendar Records !!",
                type: 'warning',
                sticky: false,
            })
        }
    }
    invisible(invisible){
        this.state.openCalendar = true
        this.state.showInvisible = invisible
    }
    async onDisplayModeChange(values, scale) {
        if(values.includes(scale)){
            return await this.updateCalender('scales', values.join(','))
        }
        return this.action.doAction({
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': "Can't remove Default Display Mode from Display Modes !!!",
                'type': 'warning',
                'sticky': false,
            }
        })
    }

    get scales() {
        return { day: "Day", week: "Week", month: "Month", year: "Year" };
    }


    async updateCalender(name, value = "") {
        this.state.openCalendar = false
        console.log()
        try {
            const response = await this.rpc("/cyllo_studio/calendar/update/attributes", {
                name,
                value,
                view_id: this.props.viewId,
                model: this.props.model.meta.resModel,
            });
            if (response) {
                let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                let cleanedStr = response.replace(/\s+/g, ' ').trim();
                storedArray.push(cleanedStr);
                sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                sessionStorage.setItem('ReDO', JSON.stringify([]));
            }
            } finally {
                this.action.doAction('studio_reload');
            }
            this.action.doAction("studio_reload");
    }

    get dateFields() {
        const dateFields = [];
        for (const [fieldName, field] of Object.entries(this.props.mode.fields)) {
            if (["date", "datetime"].includes(field.type)) {
                dateFields.push({ value: fieldName, label: field.string });
            }
        }
        return sortBy(dateFields);
    }

    get intFields() {
		const intFields = [];
		for (const [fieldName, field] of Object.entries(this.props.mode.fields)) {
			if (['integer', 'float'].includes(field.type)) {
				intFields.push({ value: fieldName, label: field.string })
			}
		}
		return [ ['', ''], ...sortBy(intFields) ];
	}

	get booleanFields() {
		const booleanFields = [];
		for (const [fieldName, field] of Object.entries(this.props.mode.fields)) {
			if (['boolean'].includes(field.type)) {
				booleanFields.push({
					value: fieldName,
					label: field.string
				})
			}
		}
		return [ ['', ''], ...sortBy(booleanFields) ];
	}

	get colourFields() {
		const colourFields = [];
		for (const [fieldName, field] of Object.entries(this.props.mode.fields)) {
			if (['many2one', 'selection', 'many2many', 'one2many'].includes(field.type)) {
				colourFields.push({
					value: fieldName,
					label: field.string
				})
			}
		}
		return [ ['', ''], ...sortBy(colourFields, (item) => item[1]) ];
	}

	get defaultDisplayFields() {
		const defaultDisplayFields = [];
		const excludedTypes = ['one2many', 'many2many', 'many2one', 'binary', 'image', 'json', 'properties_definition', 'reference'];
		for (const [fieldName, field] of Object.entries(this.props.mode.fields)) {
			if (!excludedTypes.includes(field.type)) {
				defaultDisplayFields.push({
					value: fieldName,
					label: field.string
				});
			}
		}
		return sortBy(defaultDisplayFields);
	}

    handleView(name, value = null) {
        this.state.openCalendar = false
        console.log("sa", this, name, value)
        this.props.handleView(name, value)
    }
}

CalendarOverall.components = {
  CylloStudioDropdown,
  MultiSelectDropDown,
  CalendarViewDialog,
  CylloRecordSelector,
};
