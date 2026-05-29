/** @odoo-module **/
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
const { Component, useState, useRef, useEffect, onMounted, onWillUnmount, onWillDestroy,onWillUpdateProps,useExternalListener } = owl;
import { handleUndoRedo } from "@cyllo_studio/js/utils/undo_redo_utils";

export class TextProperties extends Component {
    static template = 'cyllo_studio.TextProperties'

    setup(){
        this.rpc = useService('rpc')
        this.action = useService('action')
        this.notification = useService('effect')
        this.state = useState({
            string: this.props?.span_properties?.string || '',
            isBold:this.props?.span_properties?.bold || false,
            isItalic:this.props?.span_properties?.italic ||  false,
            isUnderline: this.props?.span_properties?.underline ||false,
            is_edit :this.props?.span_properties?.is_edit || false,

        })

        this.saveHandled = false
        this.warningCount = 0
        this.AutoSave = async (ev) => await this.handleAutoSave(ev);

        onMounted(() => {
            this.action_area= document.querySelector(".o_action_manager")
                console.log("escapeddddddddd",document.querySelector(".o_action_manager"))
                console.log("escapeddddddddd",document)
        });
        useExternalListener(document, 'click', this.AutoSave, { capture: true });
        useExternalListener(document, 'mousedown', this.AutoSave, { capture: true });

            onWillUpdateProps((nextProps) => {
            this.state.isBold = nextProps.props?.span_properties?.bold || false;
            this.state.isItalic = nextProps.props?.span_properties?.italic || false;
            this.state.isUnderline= nextProps.props?.span_properties?.underline || false;
            this.state.is_edit = nextProps.props?.span_properties?.is_edit || false;
        });

    }

    handleStyle(style){string
        if(style === 'bold'){
            if(this.state.isBold){
                this.props.element.classList.remove('fw-bold')
            } else {
                this.props.element.classList.add('fw-bold')
            }
            this.state.isBold = !this.state.isBold
        } else if(style == 'italic'){
            if(this.state.isItalic){
                this.props.element.classList.remove('fst-italic')
            } else {
                this.props.element.classList.add('fst-italic')
            }
            this.state.isItalic = !this.state.isItalic

        } else if(style == 'underline') {
            if(this.state.isUnderline){
                this.props.element.classList.remove('text-decoration-underline')
            } else {
                this.props.element.classList.add('text-decoration-underline')
            }
            this.state.isUnderline = !this.state.isUnderline
        }
    }

     handleLabelChange({target}){
         console.log("asdasdas",)
        this.props.element.textContent = target.value
        this.state.string = target.value
    }

     isElementBold() {
            const fontWeight = window.getComputedStyle(this.props.element)?.fontWeight;
            return fontWeight === 'bold' || parseInt(fontWeight) >= 500;
    }

    isElementItalic() {
            const fontStyle = window.getComputedStyle(this.props.element).fontStyle;
            return fontStyle === 'italic' || fontStyle === 'oblique';
    }

     isElementUnderlined() {
            const textDecoration = window.getComputedStyle(this.props.element).textDecorationLine;
            return textDecoration.includes('underline');

    }
    async handleAutoSave(ev) {
    console.log("this.action_area.contains(ev.target)",this.action_area.contains(ev.target))
    if (this.action_area.contains(ev.target)){
      if (ev.type === 'mousedown') {
        this.saveHandled = true;
    } else if (ev.type === 'click' && this.saveHandled) {
        this.saveHandled = false;
        return;
    }
         console.log("asdasdasdasd")
            const classArray = Array.from(this.props.element.classList);
            const updatedClassList = classArray.filter(cls => cls !== 'cy-studio-text').join(' ');
             if(this.state.is_edit){
                this.env.services.ui.block();
                try {
                    const response = await this.rpc("cyllo_studio/kanban/update/text", {
                        path: this.props.element.getAttribute("cy-xpath"),
                        view_id:this.props.span_properties.view_id,
                        model:this.props.span_properties.model,
                        view_type: this.props.span_properties.view_type,
//                        position: this.props.elementInfo.position,
                        ...this.props.viewDetails,
                        properties: {
                           string: this.state.string || '',
                           class_names: updatedClassList,

                        },

                    });
                    if(response){
                        let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                        let cleanedStr = response.replace(/\s+/g, ' ').trim();
                        storedArray.push(cleanedStr);
                        sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                        sessionStorage.setItem('ReDO', JSON.stringify([]));
                    }
                   this.env.bus.trigger("CLEAR-MENU");
                   this.notification.add({
                        title: _t("Success"),
                        message: "Text saved.",
                        type: "notification_panel",
                        notificationType: "success",
                    });
                }
                finally {
                  this.env.services.ui.unblock();

                }

            } else {
                this.env.services.ui.block();
                try {
                    console.log("edsdsd", this.props.viewDetails)

                    const response = await this.rpc("cyllo_studio/kanban/add/text", {

                        path: this.props.properties.elementInfo.path,
                        position: this.props.properties.elementInfo.position,
                        ...this.props.viewDetails,
                        properties: {
                           string: this.state.string || '',
                           class_names: updatedClassList,
                        },

                    });
                    if(response){
                        handleUndoRedo(response)
                    }
                    this.env.bus.trigger("CLEAR-MENU");
                   this.notification.add({
                        title: _t("Success"),
                        message: "Text saved.",
                        type: "notification_panel",
                        notificationType: "success",
                    });
                } finally {
                  this.env.services.ui.unblock();

                }
            }
            }
            this.action.doAction("studio_reload");

        }



}