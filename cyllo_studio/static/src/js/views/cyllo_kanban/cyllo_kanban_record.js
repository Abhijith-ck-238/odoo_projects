/** @odoo-module **/
import { KanbanRecord } from "@web/views/kanban/kanban_record";
const {useState, onMounted, useRef} = owl;
import {CylloKanbanCompiler} from "./cyllo_kanban_compiler";
import { useService } from "@web/core/utils/hooks";
import { getFormattedValue } from "@web/views/utils";
import {ColorList} from "@web/core/colorlist/colorlist";
import {_t} from "@web/core/l10n/translation";

export const scaleMapping = {
    '50%': 0.5,
    '100%': 1,
    '150%': 1.5,
    '200%': 2,
    '250%': 2.5,
    '300%': 3,
};

const { COLORS } = ColorList;

/**
 * Returns the class name of a record according to its color.
 */
function getColorClass(value) {
    return `oe_kanban_color_${getColorIndex(value)}`;
}

/**
 * Returns the index of a color determined by a given record.
 */
function getColorIndex(value) {
    if (typeof value === "number") {
        return Math.round(value) % COLORS.length;
    } else if (typeof value === "string") {
        const charCodeSum = [...value].reduce((acc, _, i) => acc + value.charCodeAt(i), 0);
        return charCodeSum % COLORS.length;
    } else {
        return 0;
    }
}

export class CylloKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.notification = useService("effect")
        this.trashRef = useRef("kanbanTrash")
        this.state = useState({
            ...this.state,
            scale: 1,
        })

        this.env.bus.addEventListener('KanbanScale', ({ detail }) => {
            this.state.scale = scaleMapping[detail.scale] || (() => {
                //@Fixme:- Fit screen not correctly fit all kanban view correctly
                //@Todo: debug the scale calculation formula
                const kanbanRenderer = document.querySelector('.o_kanban_renderer');
                const kanbanRendererComputedStyle = window.getComputedStyle(kanbanRenderer);
                if(!this.rootRef.el){
                  return 1
                }
                let width = this.rootRef.el.offsetWidth
                const kanbanRecordComputedStyle = window.getComputedStyle(this.rootRef.el);
                let marginLeft = parseFloat(kanbanRecordComputedStyle.marginLeft);
                let marginRight = parseFloat(kanbanRecordComputedStyle.marginRight);
                width = marginLeft + width + marginRight
                return parseFloat(kanbanRendererComputedStyle.width) / width;

            })();
        })

         onMounted(()=>{
            const self = this

            this.rootRef.el.addEventListener("mousemove", (el)=> {
                const elements = this.rootRef.el.querySelectorAll(".cy-studio-kanban-border");
                elements.forEach((e) => {
                  e.classList.remove("cy-studio-kanban-border");
                });
                el.target.closest('[cy-xpath]')?.classList.add('cy-studio-kanban-border')
            });

            const divElements = Array.from(this.rootRef.el.querySelectorAll('[data-drag="1"]'));

            //@Todo:- Merge both foreach together after completing the functionality
            divElements.forEach(div => {
              div.addEventListener('click', (event) => {

                if (event.target === div) {
                    const elements = document.querySelectorAll('.border-class');
                    elements.forEach(e => {
                        e.classList.remove('border-class');
                    });
                    div.classList.add('border-class')
                    const path = div.getAttribute('cy-xpath')
                    this.env.bus.trigger("CyStudioKanban-Div", {
                        view_id: this.env.config.viewId,
                        view_type: this.env.config.viewType,
                        model: this.action.currentController.props.resModel,
                        path,
                        div,
                    })

                }
              });
            });

            divElements.forEach((element, index) => {
                 var children = Array.from(element.children);
                 var nonChildDivs = divElements.filter((otherDiv) => {
                    return otherDiv !== element && !children.includes(otherDiv);
                });
                dragula([...nonChildDivs, this.trashRef.el], {
                    revertOnSpill: true,
                     moves: (el, container, handle) => {
                            const elementPath = el.getAttribute('cy-xpath')
                            const isDrag = el.getAttribute('data-drag') || false
                            const handlePath = handle.getAttribute('cy-xpath')
                            if(el.tagName.toUpperCase() === 'DIV' && isDrag && elementPath === handlePath && el.getAttribute('data-restrict')){
                                this.triggerWarning("Elements with 't-if', 't-elif', or 't-else' attributes cannot be moved.")
                                return false
                            }
                            return el.tagName.toUpperCase() === 'DIV' && isDrag && elementPath === handlePath;
                    },
                     accepts: (el, target, source, sibling) => {
                       return !el.contains(target)
                    },
                }).on('drag', (el)=> {
                     self.trashRef.el.classList.replace("opacity-0", "opacity-100");
                     nonChildDivs.forEach((e) => {
                        if(!el.contains(e)){
                            e.classList.add('cy-studio-kanban-container');
                        }
                    });
                }).on('shadow', (el, container, source)=>{
                if(container === self.trashRef.el){
                    el.classList.add('d-none')
                    self.trashRef.el.classList.replace("opacity-75", "opacity-100");
                    self.trashRef.el.style.backgroundImage = "radial-gradient(white, #fde0e0, #feaaaa)"
                } else {
                    self.trashRef.el.classList.replace("opacity-100", "opacity-75");
                    self.trashRef.el.style.backgroundImage = ""
                    el.classList.remove('d-none')
                }
                }).on('dragend', ()=>{
                    self.trashRef.el?.classList.remove("opacity-75", "opacity-100");
                self.trashRef.el.classList.add("opacity-0");
                     nonChildDivs.forEach((e) => {
                        e.classList.remove('cy-studio-kanban-container');
                    });
                }).on('drop', async(el, target, source, sibling)=>{
                    const path = el.getAttribute('cy-xpath')
                    const siblingPath = sibling?.getAttribute('cy-xpath');
                    const targetPath = target.getAttribute('cy-xpath');

                    const sibling_path = siblingPath || targetPath;
                    const position = siblingPath ? 'before' : 'inside';
                    try{
                        if(target == self.trashRef.el){
                           const response =  await self.rpc("cyllo_studio/kanban/remove", {
                                view_id: self.env.config.viewId,
                                view_type: self.env.config.viewType,
                                model: self.action.currentController.props.resModel,
                                path,
                                field_name: "",
                            })
                            if(response){
                                let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                                let cleanedStr = response.replace(/\s+/g, ' ').trim();
                                storedArray.push(cleanedStr);
                                sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                                sessionStorage.setItem('ReDO', JSON.stringify([]));
                            }

                        } else {
                            self.env.services.ui.block();
                                const response = await self.rpc("cyllo_studio/kanban/move", {
                                view_type: self.env.config.viewType,
                                model: self.action.currentController.props.resModel,
                                view_id: self.env.config.viewId,
                                path,
                                position,
                                sibling_path,
                            })
                            if(response){
                                let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                                let cleanedStr = response.replace(/\s+/g, ' ').trim();
                                storedArray.push(cleanedStr);
                                sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                                sessionStorage.setItem('ReDO', JSON.stringify([]));
                            }
                        }
                    } finally {
                        self.env.services.ui.unblock();
                    }
                    this.env.bus.trigger('resetProperties');
                    self.action.doAction('studio_reload')

                })
            });
             var drake = dragula([...divElements, this.trashRef.el], {
                revertOnSpill: true,
                moves: (el, container, handle) => {
                    if(el.getAttribute('data-restrict')){
                        this.triggerWarning("Elements with 't-if', 't-elif', or 't-else' attributes cannot be moved.")
                        return false;
                    }
                    return true;
                },
                accepts: (el, target, source, sibling) => {
                   return !el.contains(target)
                },
//                mirrorContainer:  self.rootRef.el,
            })
            drake.on('drag', ()=>{
                self.trashRef.el.classList.replace("opacity-0", "opacity-100");

                divElements.forEach((element) => {
                    element.classList.add('cy-studio-kanban-container');
                });
            }).on('shadow', (el, container, source)=>{
                if(container === self.trashRef.el){
                    el.classList.add('d-none')
                    self.trashRef.el.classList.replace("opacity-75", "opacity-100");
                    self.trashRef.el.style.backgroundImage = "radial-gradient(white, #fde0e0, #feaaaa)"
                } else {
                    self.trashRef.el.classList.replace("opacity-100", "opacity-75");
                    self.trashRef.el.style.backgroundImage = ""
                    el.classList.remove('d-none')
                }
            }).on('dragend', ()=> {
                self.trashRef.el?.classList.remove("opacity-75", "opacity-100");
                self.trashRef.el.classList.add("opacity-0");
                divElements.forEach((element) => {
                    element.classList.remove('cy-studio-kanban-container');
                });
            }).on('drop', async(el, target, source, sibling)=>{
                const path = el.getAttribute('cy-xpath')
                const fieldName = el.getAttribute('name')
                const regex = /field(\[\d+\])?$/;
                const isField = regex.test(path);
                const siblingPath = sibling?.getAttribute('cy-xpath');
                const targetPath = target?.getAttribute('cy-xpath');

                const sibling_path = siblingPath || targetPath;
                const position = siblingPath ? 'before' : 'inside';
                try{
                    self.env.services.ui.block();
                    if(target == self.trashRef.el){
                        let field = ""
                        if(isField){
                            const fieldNodes = self.props.archInfo.fieldNodes;
                            const nameExists = Object.keys(fieldNodes).filter(element => element.startsWith(fieldName));
                            let isPathIncluded = nameExists.some(name => fieldNodes[name].MainPath.includes('/kanban/field'));
                            field = isPathIncluded ? "" : fieldName
                        }

                        const response = await self.rpc("cyllo_studio/kanban/remove", {
                            view_id: self.env.config.viewId,
                            view_type: self.env.config.viewType,
                            model: self.action.currentController.props.resModel,
                            path,
                            field_name: field,
                        })
                        if(response){
                            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                            let cleanedStr = response.replace(/\s+/g, ' ').trim();
                            storedArray.push(cleanedStr);
                            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                            sessionStorage.setItem('ReDO', JSON.stringify([]));
                        }
                    } else {
                        const response = await self.rpc("cyllo_studio/kanban/move", {
                            view_type: self.env.config.viewType,
                            model: self.action.currentController.props.resModel,
                            view_id: self.env.config.viewId,
                            path,
                            position,
                            sibling_path
                        })
                        if(response){
                            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                            let cleanedStr = response.replace(/\s+/g, ' ').trim();
                            storedArray.push(cleanedStr);
                            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                            sessionStorage.setItem('ReDO', JSON.stringify([]));
                        }
                    }

                } finally {
                    self.env.services.ui.unblock();
                }
                this.env.bus.trigger('resetProperties');
                self.action.doAction('studio_reload')

             }).on('cancel', (el, container, source)=> {
                self.action.doAction('studio_reload')
            })

        })
    }

    triggerWarning(message){
        this.notification.add({
            title: _t("Validation Error"),
            message,
            type: "notification_panel",
            notificationType: "warning",
            time: 500
        });
    }

    getRecordClasses() {
        const { archInfo, canResequence, forceGlobalClick, record, progressBarState } = this.props;
        const classes = ["o_kanban_record d-flex"];
        if (canResequence) {
            classes.push("o_draggable");
        }
        if (forceGlobalClick || archInfo.openAction) {
            classes.push("oe_kanban_global_click");
        }
        if (progressBarState) {
            const { fieldName, colors } = progressBarState.progressAttributes;
            const value = record.data[fieldName];
            const color = colors[value];
            classes.push(`oe_kanban_card_${color}`);
        }
        if (archInfo.cardColorField) {
            const value = record.data[archInfo.cardColorField];
            classes.push(getColorClass(value));
        }
        return classes.join(" ");
    }

    handleSelectField(el) {
        console.log("HndlSlctdField", this, el)
        const getRestrictAttribute = (el, level = 0) => {
            if (level > 5 || !el) {
                return false; // Stop the recursion if level exceeds 5 or no element is found
            }            const isRestricted = el.getAttribute('data-restrict');
            console.log(el, isRestricted, "isRestricted", !!isRestricted)
            if (isRestricted) {
                return !!isRestricted;
            }
            return getRestrictAttribute(el.parentElement, level + 1);
        }
        const name = el.target.getAttribute("name") || el.srcElement.parentElement.getAttribute('name')
        if ( name ) {
            console.log("uihhdg", el, el.target.getAttribute("cy-xpath"), el.target.parentElement.getAttribute('cy-xpath'))
            console.log("tdtss", el.target.getAttribute("field-tag"))
            console.log("tdtss", !el.target.getAttribute("field-tag"))
            console.log("tdtss", !!el.target.getAttribute("field-tag"))
            console.log(el.target.parentElement,": INVISIBLE CONDITION ABD :",el.target)
            this.env.bus.trigger('KANBAN_FIELD_DETAILS', {
                view_id: this.env.config.viewId,
                view_type: this.env.config.viewType,
                active_fields: this.props.list.activeFields,
                model: this.action.currentController.props.resModel,
                name: name,
                path: el.target.getAttribute("cy-xpath") || el.target.parentElement.getAttribute('cy-xpath'),
                invisible: el.target.getAttribute("invisible"),
                isRestricted: getRestrictAttribute(el.target) ,
                isFieldTag: !!el.target.getAttribute("field-tag"),
                type:"KanbanFieldProperties",
                allfields:this.props.record.fields,
            });
        }
    }

    handleSelectSpan(el){
        console.log("jhdkf", el)
        console.log("jhdkf", el.target.textContent)
        console.log("jhdkf", el.target.classList.contains("fw-bold"))
        console.log("jhdkf", el.target.classList.contains("fst-italic"))
//        this.env.bus.trigger('kanbanSpanDetails', {
//            string : el.target.textContent,
//            bold: el.target.classList.contains("fw-bold"),
//            italic : el.target.classList.contains("fst-italic"),
//            underline: el.target.classList.contains("text-decoration-underline"),
//            is_edit :true ,
//            element: el.target,
//            view_id: this.env.config.viewId,
//            model: this.action.currentController.props.resModel,
//            view_type: this.env.config.viewType,
//        });
    }

    getFormattedValue(fieldId) {
        const {
            archInfo,
            record
        } = this.props;
        const {
            attrs,
            name,
            string
        } = archInfo.fieldNodes[fieldId];
        return getFormattedValue(record, name, attrs) || string;
    }

}

CylloKanbanRecord.components = {
  ...KanbanRecord.components,
};
CylloKanbanRecord.Compiler = CylloKanbanCompiler;
CylloKanbanRecord.template = "cyllo_studio.KanbanRecord";
