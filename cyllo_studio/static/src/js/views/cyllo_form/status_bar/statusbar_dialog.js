/** @odoo-module **/
import { Component, useState, useEffect, useRef } from "@odoo/owl";
import { useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { Dialog } from "@web/core/dialog/dialog";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { ExpressionEditorDialog } from "@web/core/expression_editor_dialog/expression_editor_dialog";
import { TagsList } from "@web/core/tags_list/tags_list";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { _t } from "@web/core/l10n/translation";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import {MultiSelectDropDown} from "@cyllo_studio/js/view_editor/dropdown/multi_select_dropdown/multi_select_dropdown";
import {SelectionFieldValue} from "@cyllo_studio/js/view_editor/components/selection_field_widget_vlaues/selection_field_value_widget";

console.log("SelectionFieldValue",SelectionFieldValue)
export class StatusBarDialog extends Component {
    static template = "cyllo_studio.StatusBarDialog";
    static components = {
        Dialog,
        MultiRecordSelector,
        TagsList,
        Dropdown,
        DropdownItem,
        CylloStudioDropdown,
        MultiSelectDropDown,
        SelectionFieldValue,
    };
    setup() {
       console.log("kddddddddd",this)
        this.rpc = useService('rpc');
        this.action = useService('action');
        this.dialog = useService('dialog');
        this.addDialog = useOwnedDialogs();
        this.state = useState({
            field: "existing",
            selectedField:'',
            values:[],
            isManualField:'',
            SelectedOptions:[],
            newFieldLabel:'',
            selectionValues:[''],
            existingFieldTech: "",

        })
        this.StatusBarValues = useState({
            clickable: false,
            foldField: '',
            statusbarVisible: '',
            group_ids: [],
            invisible: 'False',
            defaultValue: 'True',
        })
        this.selectionValuesRef  = useRef('cy-SelectionValues')
        this.existingSelectionRef  = useRef('cy-existingSelection')

        useEffect(()=> {
            this.state.SelectedOptions = []

            if(this.state.selectedField){
                console.log("bbbbbbbbbbbbbbbbbbbbbb")
                const field = this.props.fields[this.state.selectedField]
                console.log("sdfghj",field.selection)
                this.state.values = [ ...field.selection ] || []
                const manual = field?.manual

            }
        }, ()=> [this.state.selectedField])

    }

    ExistingField(array){
        console.log("array",array)
        const result = array.map(item => ({ value: item.name, label:item.string }));
        return result
    }
     handleExistingFieldChange(value) {
        this.state.selectedField = value;
        console.log("asdasdasdasd",this.state.selectedField)
    }

    invisibleDomain() {
    const filteredObj = {};
    for (const key in this.props.fields) {
        if (this.props.activeFields[key]) {
            filteredObj[key] = this.props.fields[key];
        }
    }
    this.addDialog(ExpressionEditorDialog, {
        resModel: this.props.model,
        fields: filteredObj,
        expression: this.StatusBarValues.invisible,
        onConfirm: (domain) => this.StatusBarValues.invisible = domain,
    });
  }
  clickOptionVisible(){

        if(!this.state.selectionValues.length || this.state.selectionValues[0] === ''){
            this.state.isOptionEmpty = true
        }
    }

  get multiSelectDropDown(){
        const values = this.state.field == 'existing' ? this.state.values : this.state.selectionValues
        let allValues = values.reduce((acc, item) => {
            if (this.state.field == 'existing'){
                acc[item[0]] = item[1];
            }else{
                acc[item] = item;
            }
          return acc;
        }, {});
        console.log("asdsdfdfd",allValues)
        console.log("asdsdfdfd",this.state.SelectedOptions)
        return {
          selectedValues:  [...new Set(this.state.SelectedOptions)],
          allValues,
          onUpdate: (value)=> {
          console.log("qwwwwwwwwwwwwwwwwklsaksa")
            this.state.SelectedOptions = value
            this.StatusBarValues.statusbarVisible = value.join(', ')
          },
//          onClickField:()=>{
//            this.clickOptionVisible()
//          }
        }
  }

  onInputLabel(ev) {
      console.log("qwqwqqw",ev)
      this.state.newFieldLabel = ev.target.value
      this.onInputTechName(ev)


    }
  onInputTechName(ev) {
        console.log("function tridertsdfsfasf",ev.target.value)
        let inputValue = ev.target.value;
        this.state.newFieldTechName = this.processTechName(inputValue);
    }
  processTechName(inputValue) {
        console.log("qwqwdqdqdqdssqdsdsd",inputValue)
        inputValue = inputValue.replace(/ /g, "_");
        inputValue = inputValue.replace(/[^a-zA-Z0-9_]/g, "");
        return inputValue.toLowerCase()
    }
  addSelectionValue(){
       if(this.state.field === 'existing'){
			return  this.state.values = [...this.state.values, ['', '']]
       }
       console.log("asdasdasdasdasdasdas",this.state.selectionValues)
		return  this.state.selectionValues = [...this.state.selectionValues, '']
    }
//  checkSelectionValues() {
//
//        let lowerCaseArray = []
//        if(this.state.field === 'existing'){
//            lowerCaseArray = this.state.values.map(element => element[0]);
//        } else{
//            console.log("else case",this.state.selectionValues)
//            lowerCaseArray = this.state.selectionValues.map(element => element.toLowerCase());
//        }
//        let setValues = new Set(lowerCaseArray);
//        console.log("ASDASD",setValues)
//        const isSameElement = setValues.size != lowerCaseArray.length
//        const isEmpty = lowerCaseArray.some(str => str === null || str.match(/^ *$/) !== null);
//        if ( isSameElement || isEmpty) {
//            let message = isSameElement ? 'Containing same values!' : 'Containing empty values!'
//            this.env.services.action.doAction({
//                'type': 'ir.actions.client',
//                'tag': 'display_notification',
//                'params': {
//                    'message': message,
//                    'type': 'warning',
//                    'sticky': false,
//                }
//            })
//            this.state.isDefaultOk = "False"
//            return false
//
//        }
//        this.state.isDefaultOk = "True"
//        return true
//    }
  changeSelectionValue(index, value){

        console.log(123123., index, value)

        this.state.isOptionEmpty = false
        let optionsIndex = -1
        if(this.state.field === "existing"){
            optionsIndex = this.state.SelectedOptions.indexOf(this.state.values[index][0])
        } else {
            optionsIndex = this.state.SelectedOptions.indexOf(this.state.selectionValues[index])
        }
        if (optionsIndex !== -1){
            this.state.SelectedOptions[optionsIndex] = value
        }
        if(this.state.field === "existing"){
            this.state.values[index][1] = value
            const field = this.props.fields[this.state.existingFieldTech]

            if(!field.selection.some((item) => item[0] === this.state.values[index][0])){
                this.state.values[index][0] = value.toLowerCase()
            }
        } else {
            this.state.selectionValues[index] = value
             let lowerCaseArray = []
            lowerCaseArray = this.state.selectionValues.map(element => element.toLowerCase());
            let setValues = new Set(lowerCaseArray);
            const isSameElement = setValues.size != lowerCaseArray.length
            const isEmpty = lowerCaseArray.some(str => str === null || str.match(/^ *$/) !== null);
            if ( isSameElement || isEmpty) {
                this.state.isDefaultOk = "False"

            }
            else{
                this.state.isDefaultOk = "True"
                }

            }
    }
  async deleteSelectionValue(index){
        const optionsIndex = this.state.SelectedOptions.indexOf(
                    this.state.field === "existing" ? this.state.values[index][0] :this.state.selectionValues[index])
        if(this.state.field === "existing"){
            const field = this.props.fields[this.state.existingFieldTech]
            if(field.selection.some((item) => item[0] === this.state.values[index][0])){
                const confirm = await new Promise((resolve) => {
                    this.dialog.add(ConfirmationDialog, {
                        title: _t("Are you sure ?"),
                        body: _t("The value will be removed from all records"),
                        confirmLabel: _t("Yes"),
                        confirm: resolve.bind(null, true),
                    }, {
                        onClose: resolve.bind(null, false),
                    });
                })
                if(!confirm){
                    return false
                }
            }
            this.state.values.splice(index, 1)
        } else {
            this.state.selectionValues.splice(index, 1)
        }
         if (optionsIndex !== -1){
            this.state.SelectedOptions.splice(optionsIndex, 1)
        }
    }

    get existingFields() {
        const selectionFields = Object.entries(this.props.fields)
            .filter(([key, field]) => field.type === "selection" && field.store)
            .map(([key, field]) => ({ name: field.name, string: field.string }));
        return selectionFields
    }

    DefaultValueExistingField(array){
        const result = array.map(item => ({ value: item[0], label:item[1] }));
        return result
    }

    handleDefaultValueExisting(value) {
        this.StatusBarValues.defaultValue = value;
    }
    get defaultExistingField() {
        return this.state.existingFieldTech
     }
     get DefaultValueNewField(){
        const arr = []
        for(let value in this.state.selectionValues){
            const obj = { value : this.state.selectionValues[value] ,label:this.state.selectionValues[value] }
            arr.push(obj)
        }
        return arr
    }
    handleDefaultValueNewField(value) {
        this.StatusBarValues.defaultValue = value;
    }
    async onConfirm() {
    console.log("this.state.field", this.state.field);

    // Prepare the initial values object
    let values = {
        path: this.props.path,
        view_id: this.props.viewId,
        is_new: false,
        model: this.props.model,
        view_type: 'form',
        header: this.props.header,
        field: this.state.selectedField, // Default field
    };

    let kwargs = { ...this.StatusBarValues };

    // Handle the case when a new field is being added
    if (this.state.field === 'new') {
        const { newFieldLabel, newFieldTechName, selectionValues } = this.state;

        if (!newFieldLabel || !newFieldTechName) {
            return this.actionWarning('Both fields are required');
        }

        // Update values for the new field
        values = {
            ...values,
            field: `x_cy_${newFieldTechName}`, // Construct field name
            label: newFieldLabel, // Use label separately
            is_new: true,
        };

        kwargs.values = selectionValues;
    }

    // Block the UI to prevent further actions while processing
    this.env.services.ui.block();

    try {
        // Make the RPC call to add the status bar
        const response = await this.rpc("cyllo_studio/add/statusbar", { args: { ...values }, kwargs });

        if (response) {
            const cleanedResponse = response.replace(/\s+/g, ' ').trim();
            const storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];

            // Append the cleaned response to the undo stack
            storedArray.push(cleanedResponse);
            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
            sessionStorage.setItem('ReDO', JSON.stringify([])); // Reset redo stack
        }
    } catch (error) {
        console.error("Error while adding status bar:", error);
        // Optionally handle the error (e.g., show a user-friendly message)
    } finally {
        // Unblock the UI after processing
        this.env.services.ui.unblock();
    }

    // Perform the action and close the dialog
    this.action.doAction('studio_reload');
    this.props.close();
}
    actionWarning(message) {
        return this.action.doAction({
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                    'message': message,
                'type': 'warning',
                'sticky': false,
            }
        })
    }


    onDiscard() {
        this.props.close();
    }

}