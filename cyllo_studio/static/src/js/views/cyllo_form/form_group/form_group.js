/** @odoo-module */
const {
    useState,
    useRef,
    onMounted
} = owl
import {
    InnerGroup, OuterGroup
} from "@web/views/form/form_group/form_group";
import {
    registry
} from "@web/core/registry";
import {
    patch
} from '@web/core/utils/patch';
import {
    useService
} from "@web/core/utils/hooks";
import {
    EventBus
} from "@odoo/owl";

OuterGroup.props = [
    ...OuterGroup.props,
    "cy-xpath?"];
OuterGroup.template = "cyllo_studio.Form.StudioOuterGroup";


//export class CylloOuterGroup extends OuterGroup {
//    static template = "cyllo_studio.Form.StudioOuterGroup";
//    setup() {
//        super.setup();
//        console.log("hjdkrkkkkkkkkkkkkkkkkkkk", this)
//        this.bus = new EventBus();
//        const viewService = useService("view");
//        var elOuterHTML = localStorage.getItem('elouterHTML')
////        var path = XpathExtract(elOuterHTML, '//group')
//        this.rpc = useService("rpc");
//        var self = this
//        this.root = useRef("cy-OuterRoot");
//        this.action = useService("action");
//        this.viewService = useService("view");
//    }
//}
export class CylloInnerGroup extends InnerGroup {
    static template = "cyllo_studio.Form.StudioInnerGroup";
    setup() {
        super.setup();
        console.log("hjdkr", this)
        this.rpc = useService("rpc");
        this.state = useState({
            hover: false,
            addField: true,
            panelMenu: '',
            sibling: '',
        });
//        this.content = registry.category("cyllo_studio_widget_list").get("widget_list")
        this.action = useService("action");
        onMounted(() => {
            this.env.bus.trigger("allWidgets", {
                widgets: this.content,
            });
        });
    }
    over(ev) {
        this.state.hover = true
    }
    overoff(ev) {
        this.state.hover = false
    }
    onAddClick(ev) {
        this.state.sibling = !this.state.sibling
        ev.target.classList.toggle('ri-add-circle-line');
        ev.target.classList.toggle('ri-close-circle-line');
    }
    addSibling(ev, cell) {
        let parent = ev.target.closest(".o_wrap_field");
        let path = parent?.firstElementChild.getAttribute("cy-xpath");
        let itemType = 'normal'
        let fieldInfo = {}
        if (!path) {
            let child = parent?.firstElementChild
            if (child?.firstElementChild.nodeName == 'BUTTON') {
                return false;
                path = child?.firstElementChild.getAttribute('cy-xpath')
            } else {
                itemType = 'o_row'
                path = child.nextElementSibling?.firstElementChild.getAttribute('cy-xpath')
            }
        } else {
            fieldInfo = {
                string: cell.props.fieldInfo?.string,
                name: cell.props.fieldInfo?.name,
                help: cell.props.fieldInfo?.help,
                widget: cell.props.fieldInfo?.widget,
                placeholder: cell.props.fieldInfo?.placeholder,
                invisible: cell.props.fieldInfo?.invisible,
                readonly: cell.props.fieldInfo?.readonly,
                required: cell.props.fieldInfo?.required,
                context: cell.props.fieldInfo?.context,
                options: cell.props.fieldInfo?.options,
                domain: cell.props.fieldInfo?.domain,
            }
        }

        if (path) {
            this.env.bus.trigger("Sibling", {
                path,
                position: 'insert',
                fieldInfo,
                itemType,
            });
        }
    }
    handlePanelMenu(ev) {
        if (ev.target.parentElement.nextElementSibling) {
            this.state.panelMenu = false
        } else {
            this.state.panelMenu = true
        }
        ev.target.classList.toggle('ri-arrow-left-s-fill');
        ev.target.classList.toggle('ri-arrow-right-s-fill');
    }
    async deleteElement(ev) {
        let parent = ev.target.closest(".o_wrap_field");
        let item_path = parent.firstElementChild.getAttribute("cy-xpath") || "";
        let has_multipath = false;
        if (!item_path) {
            let child = parent.firstElementChild;
            if (child.firstElementChild.nodeName == "BUTTON") {
                item_path = child.firstElementChild.getAttribute("cy-xpath");
            } else {
                has_multipath = true;
                item_path = {
                    first_path: child.firstElementChild.getAttribute("cy-xpath"),
                    second_path: child.nextElementSibling?.firstElementChild.getAttribute("cy-xpath"),
                };
            }
        }

        this.env.services.ui.block();
        try {
            const response = await this.rpc("/cyllo_studio/remove/form_element", {
                item_path,
                has_multipath,
                model: this.env.model.config.resModel,
                view_id: this.env.config.viewId,
            });
            if (response) {
                let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                let cleanedStr = response.replace(/\s+/g, ' ').trim();
                storedArray.push(cleanedStr)
                sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                sessionStorage.setItem('ReDO', JSON.stringify([]));
            }
        } finally {
            this.env.services.ui.unblock();
        }
        this.env.bus.trigger('resetProperties');
        this.action.doAction("studio_reload");
    }
    async itemOnDelete(ev) {
        this.env.bus.trigger('resetProperties');
        const view_id = this.env.model.env.searchModel.env.config.viewId;
        const response = await this.env.model.rpc("cyllo_studio/delete/component", {
            method: "delete_component",
            model: this.env.model.config.resModel,
            view_id: this.env.model.env.searchModel.env.config.viewId,
            view_type: "form",
            args: [],
            kwargs: {
                viewType: "form",
                path: ev.target.parentElement.parentElement.attributes["cy-xpath"]
                    .value,
                model: this.env.model.config.resModel,
                view_id: view_id ? view_id : null,
            },
        });
        if (response) {
            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
            let cleanedStr = response.replace(/\s+/g, ' ').trim();
            storedArray.push(cleanedStr)
            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
            sessionStorage.setItem('ReDO', JSON.stringify([]));
        }
        this.action.doAction("studio_reload");
    }

}
var value = window.location.href
var searchParams = new URLSearchParams(value.split("?")[1]);
CylloInnerGroup.props = [...InnerGroup.props, "cy-xpath?"];
//CylloInnerGroup.template = "cyllo_studio.Form.CylloInnerGroup";
