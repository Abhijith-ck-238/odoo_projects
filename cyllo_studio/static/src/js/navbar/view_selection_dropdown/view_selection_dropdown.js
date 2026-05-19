/** @odoo-module **/
import {
    Component,
    useState,
    onMounted,
    onWillStart,
    useRef
} from "@odoo/owl";
import {
    useService
} from "@web/core/utils/hooks";
import { CalendarDialog } from "@cyllo_studio/js/view_editor/dialog/calendar_dialog";
const ICONCLASS = {
    list: "ri-align-justify",
    form: "ri-profile-line",
    activity: "ri-time-line",
    search: "ri-search-eye-line",
    kanban: "ri-bar-chart-2-fill",
    calendar: "ri-calendar-2-fill",
    pivot: "ri-table-2",
    gantt: "fa fa-tasks",
    graph: "ri-line-chart-line",
    map_view: "fa fa-map-marker",
};

const ViewTypes = [
    "list",
    "kanban",
    "form",
    "activity",
    "graph",
    "pivot",
    "search",
    "calendar",
];

export class ViewSelectionDropDown extends Component {
    static template = "cyllo_studio.ViewSelectionDropDown";
    setup() {
        this.state = useState({
            activatedViews: [],
        });
        this.ViewTypes = ViewTypes;
        this.viewIcons = ICONCLASS;
        this.root = useRef("root");
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.orm = useService("orm");
        this.dialogService = useService("dialog");

        onWillStart(async() => {
//            if (sessionStorage.getItem('CylloDefaultView')) {
//                this.state.defaultView = sessionStorage.getItem('CylloDefaultView')
//                sessionStorage.removeItem('CylloDefaultView');
//            } else {
////                this.state.defaultView = await this.action.currentController.config.views?.[0][1]
//            }
        })

        onMounted(async () => {
//            this.state.dropdowns = this.root.el.querySelectorAll(".hnk-dropdown");
            await this.env.bus.addEventListener("ACTIVE-VIEWS", ({ detail }) => {
                this.state.activatedViews = (detail.views || []).map(view => view[1]);
                this.state.defaultView = sessionStorage.getItem('CylloDefaultView') || detail.views[0][1]
                sessionStorage.removeItem('CylloDefaultView');
            });
            const url = new URL(window.location.href);
            const hashParams = new URLSearchParams(url.hash.slice(1)); // Remove "#" and parse
            const model = hashParams.get("model");
            const activity = await this.orm.searchRead("ir.model", [
                ["model", "=", model],
                ["is_mail_activity", "=", true],
            ], ["is_mail_activity", "state"]);
            this.state.activity = activity[0] ? true : false
            window.addEventListener("click", (e) => {
                if(this.root.el?.querySelector(".hnk-dropdown--open")){
                    this.closeDropdown.bind(this)(e);
                }
            });
        });
    }
    onViewClicked(view) {
        this.action.switchView(view);
        const viewFlags = { editButton: true, edit: false, viewChanged: true };
        for (const [key, value] of Object.entries(viewFlags)) {
            this.props.viewChange(key, value);
        }
        sessionStorage.removeItem("cyStudioSearch");
    }
    onSearchClick() {
        this.env.bus.trigger("SEARCH_CLICKED");
        this.props.viewChange("editButton", false);
    }
    toggleViewDropdown(e) {
        const parent = document.querySelector(".hnk-dropdown");
        if (!parent) return;
        parent.classList.toggle("hnk-dropdown--open");
    }
    closeDropdown(e) {
        const clickedDropdown = e.target.closest(".hnk-dropdown");
        if (!clickedDropdown) {
            this.root.el?.querySelectorAll(".hnk-dropdown").forEach(dropdown =>
                dropdown.classList.remove("hnk-dropdown--open")
            );
        }
    }
    async onClickBox(e) {
        const activeView = e.target.checked
        const viewType = e.target.attributes.target.value
        if (this.action.currentController.config.actionId) {
            if (this.state.activatedViews.length <= 2 && !activeView && viewType !== 'search') {
                e.target.checked = true;
                return this.action.doAction({
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'At least one view is required.',
                        'type': 'warning',
                        'sticky': false,
                    }
                })
            }
            if (viewType !== 'calendar' || !activeView) {
                await this.rpc("/cyllo_studio/view/active_views", {
                    args: [{
                        activeView,
                        actionId: this.action.currentController.config.actionId,
                        actionType: this.action.currentController.config.actionType,
                        viewType,
                        resModel: this.action.currentController.action.res_model,
                        name: this.action.currentController.action.name,
                    }]
                })
//                const invisible_session = sessionStorage.getItem('invisible');
//                if (invisible_session) {
//                    sessionStorage.removeItem('invisible')
//                    await this.rpc("cyllo_studio/find/invisible", {
//                        method: 'find_invisible_fields',
//                        args: [{
//                            invisible: false
//                        }],
//                        kwargs: {}
//                    })
//                }
                window.location.reload()
            } else if (activeView) {
                const allFields = this.__owl__.parent.parent.children.__2.children.__1.component.overall.allFields || this.__owl__.parent.parent.children.__2.children.__1.component.overall.activeFields
                this.dialogService.add(CalendarDialog, {
                    fields: allFields,
                    details: [{
                        activeView,
                        actionId: this.action.currentController.config.actionId,
                        actionType: this.action.currentController.config.actionType,
                        viewType,
                        resModel: this.action.currentController.action.res_model,
                        name: this.action.currentController.action.name,
                    }]
                })
            }
        }
    }

    async handleDefaultView(ev) {
        const parentElement = ev.target.parentElement
        const siblings = Array.from(parentElement.children).filter((child) => child !== ev.target);
        const siblingWithType = siblings.find((sibling) => sibling.hasAttribute('target'));
        const siblingType = siblingWithType.getAttribute('target')
        this.result = await this.rpc("/cyllo_studio/view/active_views/set_default_view", {
            args: [{
                'actionId': this.action.currentController.config.actionId,
                'siblingType': siblingType,
            }]
        })
        this.state.defaultView = siblingType
            sessionStorage.setItem('CylloDefaultView', this.state.defaultView);
        this.action.doAction('studio_reload')
    }
}
