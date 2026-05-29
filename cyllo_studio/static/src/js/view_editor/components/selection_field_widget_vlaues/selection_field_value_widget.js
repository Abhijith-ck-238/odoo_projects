/** @odoo-module **/
import { Component, useState, useEffect, onWillUpdateProps } from "@odoo/owl";

export class SelectionFieldValue extends Component {

    setup() {
        console.log("setuped succesfully",this)
        this.state = useState({
//            edit: true,
            value: this.props.value,
        });

        useEffect(()=> {
            console.log(234234,this.props.index, this.state.value)
            this.props.changeValue(this.props.index, this.state.value)
        }, ()=> [this.state.value])

        onWillUpdateProps((nextProps) => {
            this.state.value = nextProps.value
        });
    }

//    toggle() {
//        if (this.state.edit) {
//            if (!this.props.checkSelectionValues()){
//                return null
//            }
//        }
//        this.state.edit = !this.state.edit
//    }
}

SelectionFieldValue.template = "cyllo_studio.SelectionFieldValue"