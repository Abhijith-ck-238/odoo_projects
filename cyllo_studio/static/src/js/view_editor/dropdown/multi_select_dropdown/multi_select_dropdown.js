/** @odoo-module **/
import { Component, useState, onWillUpdateProps } from "@odoo/owl";

import { TagsList } from "@web/core/tags_list/tags_list";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { Dropdown } from "@web/core/dropdown/dropdown";
export class MultiSelectDropDown extends Component {
    static template = "cyllo_studio.MultiSelectDropDown";
    static components = {
        TagsList,
        Dropdown,
        DropdownItem,
    };
    static props = {
        selectedValues: { type: Array, optional: true },
        allValues: { type: Object, optional: false },
        onUpdate: { type: Function, optional: false },
        class: { type: String, optional: true },
        style: { type: String, optional: true },
    };
    setup() {
        this.state = useState({
            selectedValues: this.props.selectedValues,
            allValues: this.props.allValues
        })
        onWillUpdateProps((nextProps)=> {
            this.state.allValues = nextProps.allValues
            this.state.selectedValues = nextProps.selectedValues
        })
    }

    onSelected(value) {
       this.props.onUpdate([...this.state.selectedValues, value])
    }


    getTagProps(rec) {
        return {
            id: rec,
            text: this.state.allValues[rec],
            onDelete: () => this.deleteTag(rec),
        };
    }

    deleteTag(rec) {
        this.props.onUpdate(this.state.selectedValues.filter(item => item !== rec))
    }

    get tags() {
        let vals = this.state.selectedValues.map((rec, index) => {
            return this.getTagProps(rec)
        })
        return vals || {}
    }
}
