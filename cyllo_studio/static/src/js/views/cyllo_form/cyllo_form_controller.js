/** @odoo-module **/
import { FormController } from "@web/views/form/form_controller";
import { evaluateBooleanExpr } from "@web/core/py_js/py";
import { Layout } from "@web/search/layout";
import { useService } from "@web/core/utils/hooks";
import { CylloListRenderer } from "@cyllo_studio/js/views/cyllo_list/cyllo_list_renderer";
import { CylloKanbanRenderer } from "@cyllo_studio/js/views/cyllo_kanban/cyllo_kanban_renderer";
import { serializeXML } from "@web/core/utils/xml";
import { onWillStart, useEffect, useState } from "@odoo/owl";

export class CylloFormController extends FormController {
    async setup() {
        super.setup();
        console.log("FormCtrl", this)
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.fieldMove = useState({
            toggle: false,
//            firstReload: true,
        });
        this.state = useState({
            isX2Many: false,
//            CyX2Many: false,
            x2ManyDetails: {}
        })
        onWillStart(async ()=>{
            console.log("djxk", this)
//            this.env.bus.trigger("Studio:NotebookChanged")
//            if(!this.env.config.viewId){
//                await this.rpc('cyllo_studio/form/add/form_view',{
//                    arch: serializeXML(this.props.arch),
//                    model: this.props.resModel,
//                })
//                sessionStorage.setItem('CyStudioView', this.props.resModel)
//                await this.action.doAction('studio_reload')
//            }
        })
//        const Propsstate = this.props.state || {};
//        const activeNotebookPages = {
//            ...Propsstate.activeNotebookPages
//        };
//        this.onNotebookPageChange = (notebookId, page) => {
//            if (page) {
//                this.fieldMove.toggle = !this.fieldMove.toggle;
//                activeNotebookPages[notebookId] = page;
//            }
//        };

    useEffect(() => {
        console.log("Jjkjf", this)
        const self = this;
        const InGrps = document.getElementsByClassName("o_inner_group");
        console.log("InGrps", InGrps)
        const drake = dragula([...InGrps], {
            revertOnSpill: true,
            moves: function(el, container, handle) {
                console.log("MoVes", el)
                console.log("MoVes", container)
                console.log("MoVes", handle)
//                || el.classList.contains("add-fields") //Todo removed from below if, className add-fields is not in any form related files
                if (handle.classList.contains("cy-studio-icon") || el.children.length > 2) {
                    return false;
                }
                return el.classList.contains("o_wrap_field");
            },
            accepts: function(el, target, source, sibling) {
                if (!sibling || sibling.classList.contains('o_wrap_field') || sibling.classList.contains('o_cell')|| sibling.classList.contains('cy-inner-trash-container')) {
                    return true;
                }
                return false;
            },
        });
        let initialIndex = ''
        let initialX = ''
        drake.on("drag", (el,source) => {
            initialIndex = Array.from(source.children).indexOf(el);
            initialX = el.getBoundingClientRect().left;
            const elementIcon = el.querySelector(".cy-studio-field-icons");
            console.log("ElementIcon", elementIcon)
            elementIcon?.classList.add("d-none");
            el.classList.remove("d-sm-contents", "flex-column");
            if (el.children.length > 1) {
                [el.children[0], el.children[1]].forEach((child, index) => {
                    child?.classList.add(
                        "col-6",
                        "border",
                        "border-primary",
                        "w-100",
                        "h-100"
                    );
                    if (index === 0) child.classList.add("me-3");
                    // if (index === 1) child.classList.add("ms-3"); // Uncomment if needed
                });
            } else {
                el.children[0]?.classList.add("col-12", "border", "border-primary");
            }
            console.log("ElChild0", el.children[0].classList)
            console.log("ElChild1", el.children[1].classList)
            console.log("Draagg", el)
            console.log("Draagg", source)
        })
        .on("over", function(el, container, source) {
            el.classList.add("d-sm-contents", "flex-column");
        })
        .on("dragend", function(el, container) {
            const elementIcon = el.querySelector(".cy-studio-field-icons");
            elementIcon?.classList.remove("d-none");
            el.classList.add("d-sm-contents", "flex-column");
            const classesToRemove = ["border", "border-primary"];
            if (el.children.length > 1) {
                [el.children[0], el.children[1]].forEach(child =>
                    child?.classList.remove("col-6", ...classesToRemove)
                );
            } else {
                el.children[0]?.classList.remove("col-12", ...classesToRemove);
            }
        })
        .on("drop", async (el, target, source, sibling) => {
            let finalIndex = Array.from(target.children).indexOf(el);
            let finalX = el.getBoundingClientRect().left;
            console.log("OIioioi", finalIndex)
            console.log("OIioioi", finalX)
            let path = target?.getAttribute("cy-xpath");
            let position = sibling ? "before" : "inside";
            if (sibling) {
                if (sibling.classList.contains("cy-inner-trash-container")) {
                    path = sibling.nextElementSibling?.firstElementChild?.getAttribute("cy-xpath") ||
                           sibling.nextElementSibling?.firstElementChild?.firstElementChild?.getAttribute("cy-xpath");
                } else {
                    path = sibling.firstElementChild?.getAttribute("cy-xpath");
                }
                if (!path) {
                    path = sibling.firstElementChild?.firstElementChild?.getAttribute("cy-xpath");
                }
            }
            let has_multipath = false;
            let item_path = el.firstElementChild?.getAttribute("cy-xpath") || "";
            console.log("ItemPathhhh1", item_path)
            if (!item_path) {
                const child = el.firstElementChild;
                console.log("CChiLD", child)
                console.log("CChiLD", child.nextElementSibling)
                console.log("CChiLD", child.firstElementChild)
                const firstChild = child?.firstElementChild;
                console.log("ItemPathhhh2", item_path)

                if (firstChild?.nodeName === "BUTTON") {
                    item_path = firstChild.getAttribute("cy-xpath");
                    console.log("ItemPathhhh3", item_path)
                } else if (!child?.nextElementSibling) {
                    item_path = firstChild?.getAttribute("cy-xpath");
                    console.log("ItemPathhhh4", item_path)
                } else {
                    has_multipath = true;
                    item_path = {
                        first_path: firstChild?.getAttribute("cy-xpath"),
                        second_path: child.nextElementSibling?.firstElementChild?.getAttribute("cy-xpath"),
                    };
                    console.log("ItemPathhhh5", item_path)
                }
            }
            let direction =
            finalX > initialX ? "right" :
            finalX < initialX ? "left" :
            finalIndex > initialIndex ? "down" :
            finalIndex < initialIndex ? "up" :
            "";
            console.log("Directoiponh", direction)
            console.log("Directoiponh", item_path)
            if (path) {
                self.env.services.ui.block();
                try {
                    const args = {
                        'item_path': item_path,
                        'path': path,
                        'position': position,
                        'has_multipath': has_multipath,
                        'model': self.props.resModel,
                        'view_id': self.env.config.viewId,
                        'direction': direction,
                        'inSource': target === source,
                    }
                    const result = await self.rpc("/cyllo_studio/FieldPositionMove", {args});

                    if (result) {
                        const storedArray = JSON.parse(sessionStorage.getItem("UndoRedo")) || [];
                        storedArray.push(result.FormArch.replace(/\s+/g, " ").trim());
                        sessionStorage.setItem("UndoRedo", JSON.stringify(storedArray));
                        sessionStorage.setItem("ReDO", "[]");
                    }
                } finally {
                    self.env.services.ui.unblock();
                }
            }
            self.action.doAction("studio_reload");
            this.env.bus.trigger('CLEAR-MENU');
        })
    }, () => [this.fieldMove.toggle]);

    }
}
