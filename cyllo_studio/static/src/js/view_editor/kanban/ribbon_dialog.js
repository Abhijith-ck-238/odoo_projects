/** @odoo-module **/
import { Dialog } from "@web/core/dialog/dialog";
const { Component, onWillStart, useState, useEffect, onMounted, useRef } = owl;
import {useService, useOwnedDialogs} from "@web/core/utils/hooks";
import { ExpressionEditorDialog } from "@web/core/expression_editor_dialog/expression_editor_dialog";

export class RibbonDialog extends Component {
    static template = 'cyllo_studio.RibbonDialog'
    static components = {
        Dialog
    }
    static props = [
      'ribbonElement',
      'fields',
      'viewDetails',
      'close'
    ]
    setup(){
        this.state = useState({
            ribbons: [],
            selectedIndex: 0,
            hasEdit: false,
            showDropdown: false,
        })
        this.addDialog = useOwnedDialogs();
        this.previewRef = useRef('PreviewRef')
        onMounted(() => {
//            this.state.ribbons = Array.from(this.props.ribbonElement).map(this.getElementDetails.bind(this));
//            const element = this.state.ribbons[this.state.selectedIndex].element;
//            this.addPreviewStyle()
        })

        this.rpc = useService('rpc')
        this.action = useService('action')

    }

//    get colors(){
//        return {
//            'text-bg-primary': 'Primary',
//            'text-bg-secondary': 'Secondary',
//            'text-bg-success': 'Success',
//            'text-bg-info': 'Info',
//            'text-bg-warning': 'Warning',
//            'text-bg-danger': 'Danger'
//        }
//    }

    // Function to check if an element or its children contain any of the specified attributes
//    hasConditionAttributes(element){
//        const conditionAttributes = ['data-t-if', 'data-t-else', 'data-t-elif'];
//
//        // Check the element itself
//        for (let attr of conditionAttributes) {
//            if (element.hasAttribute(attr)) {
//                return true;
//            }
//        }
//
//        // Check the children
//        for (let child of element.children) {
//            for (let attr of conditionAttributes) {
//                if (child.hasAttribute(attr)) {
//                    return true;
//                }
//            }
//        }
//
//        return false;
//    }

//   getElementDetails(element, index) {
//    const children = element.children;
//    const hasConditionAttributes = this.hasConditionAttributes(element);
//
//    let firstElementContent = null, firstElementPath = null, firstElementClass = null, color = null;
//
//    // Loop through children to find the first valid one with content
//    for (let i = 0; i < children.length; i++) {
//        const child = children[i];
//        const childText = child.textContent.trim();
//        if (childText) {
//            firstElementContent = childText;
//            firstElementPath = child.getAttribute('cy-xpath');
//            firstElementClass = child.className;
//            color = Array.from(child.classList).find(cls => cls.startsWith('text-bg-'));
//            break;
//        }
//    }
//
//    console.log("First Element Content:", firstElementContent);
//
//    return {
//        arrayIndex: index,
//        path: element.getAttribute('cy-xpath'),
//        invisible: element.getAttribute('data-invisible'),
//        hasMultipleChildElement: children.length > 1,
//        class: firstElementClass,
//        color,
//        firstElementContent,
//        firstElementPath,
//        hasDelete: false,
//        hasEdit: false,
//        hasConditionAttributes,
//        element
//    };
//}


//    onDomainRadioClick({target}){
//        this.state.ribbons[this.state.selectedIndex].hasEdit = true
//        this.state.ribbons[this.state.selectedIndex].invisible = target.checked ? 'True' : 'False'
//    }

//    handleSelectColor(color){
//        this.state.ribbons[this.state.selectedIndex].hasEdit = true
//        this.state.ribbons[this.state.selectedIndex].color = color
//        this.state.showDropdown = false
////        this.state.ribbons[this.state.selectedIndex].element.firstChild.className = color
//        this.addPreviewStyle()
//    }

//     onChangeText(value){
//        this.state.ribbons[this.state.selectedIndex].hasEdit = true
//        this.state.ribbons[this.state.selectedIndex].firstElementContent = value
//        this.addPreviewStyle()
//    }

//    onDomainClick() {
//        this.state.ribbons[this.state.selectedIndex].hasEdit = true
//        this.addDialog(ExpressionEditorDialog, {
//          resModel: this.props.viewDetails.model,
//          fields: this.props.fields,
//          expression: this.state.ribbons[this.state.selectedIndex].invisible,
//          onConfirm: (expression) => this.state.ribbons[this.state.selectedIndex].invisible = expression,
//        });
//    }

//    addPreviewStyle(){
//        const ribbon = this.state.ribbons[this.state.selectedIndex]
//        this.previewRef.el.innerHTML = ribbon.firstElementContent
//        this.previewRef.el.className = ribbon.color
//    }

//    handleRibbon(index){
//        this.state.selectedIndex = index
//        const element = this.state.ribbons[index].element;
//        this.addPreviewStyle()
//    }

//    handleDelete(index){
//        this.state.ribbons[index].hasDelete = true
//    }

//    handleEdit(ribbon){
//        this.state.hasEdit = true
//        this.state.selectedIndex = ribbon.arrayIndex
//        this.addPreviewStyle()
//    }

//    handleDone(){
//        if(this.state.ribbons[this.state.selectedIndex].firstElementContent){
//        console.log("eef")
//        this.state.hasEdit = false
//        }
//        else{
//                console.log("sce")
//
//        return this.action.doAction({
//           'type': 'ir.actions.client',
//           'tag': 'display_notification',
//           'params': {
//               'message': 'The label should not be empty',
//               'type': 'warning',
//               'sticky': false,
//           }
//        })
//        }
//    }

//    filterAndModifyArray(ribbons){
//        return ribbons
//            .filter(item => item.hasDelete || item.hasEdit)
//            .map(({ element, ...rest }) => rest);
//    }

//    async handelSave(){
//        const ribbons = this.filterAndModifyArray(this.state.ribbons).reverse()
//         const response = await this.rpc('cyllo_studio/kanban/update/ribbons',{
//            ...this.props.viewDetails,
//            ribbons
//        })
//        if(response){
//            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
//            let cleanedStr = response.replace(/\s+/g, ' ').trim();
//            storedArray.push(cleanedStr);
//            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
//            sessionStorage.setItem('ReDO', JSON.stringify([]));
//        }
//        this.action.doAction('studio_reload')
//        this.props.close()
//    }

    handelDiscard(){
        this.props.close()
    }
}