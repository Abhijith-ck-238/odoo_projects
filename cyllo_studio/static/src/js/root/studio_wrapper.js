/** @odoo-module **/
import {
    Component,
    useState
} from "@odoo/owl";
import {
    useBus
} from "@web/core/utils/hooks";
import {
    AsideBar
} from "@cyllo_studio/js/view_editor/aside_bar/aside_bar";
import {
    MenuSideBar
} from "@cyllo_base/js/menu_sidebar";
import {
    StudioMenuSideBar
} from "@cyllo_studio/js/studio_menu_sidebar/studio_menu_sidebar";
import {
    MainComponentsContainer
} from "@web/core/main_components_container";
import {
    ExistingFieldDialog
} from "@cyllo_studio/js/view_editor/aside_bar/dialog/existing_field_dialog";
import {
    useService
} from "@web/core/utils/hooks";
import {
    ActivityDialog
} from "@cyllo_studio/js/views/cyllo_activity/cyllo_activity_dailog";

export class StudioWrapper extends Component {
    static template = "cyllo_studio.StudioWrapper";
    static props = {
        updateState: {
            type: Function,
            optional: true
        },
        info: {
            type: Object,
            optional: true
        },
        viewChanged: {
            type: Boolean,
            optional: true
        },
        edit: {
            type: Boolean,
            optional: true
        },
    };
    setup() {
        this.state = useState({
            isAnimatingSidebar: false,
            activity_view: false,
        });
        this.dialogService = useService("dialog");
        this.action = useService('action');
        this.overall = useState({
            mode: {},
            allFields: {},
            activeFields: {},
            edit: this.props.edit,
            measure: {},
            isMenu: false,
            progressAttributes: {},
            envModel: {},
            ribbonElement: document.querySelectorAll("nonexistent-selector"),
            MetaData: {},
            calendar_info: {},
            model: ''
        });
        this.viewDetails = useState({
            model: "",
            viewId: 0,
            viewType: "",
            type: "",
            allFields: {}
        });
        this.fieldProperties = useState({
            attr: {},
            name: "",
            label: "",
            widget: "",
            fieldType: "",
            context: "",
            related_model: "",
            edit: "",
            path: "",
            help: "",
            placeholder: "",
            invisible: "",
            readonly: "",
            create: "",
            field_path: "",
            widget_types: [],

        });
        this.kanbanComponent = useState({
            properties: "",
            item: "",
            element: "",

        });
        this.buttonInfo = useState({
            type: "",

        });
        this.noteBookProperties = useState({
            properties: "",
            type: "",

        });
        this.SmartButtonProperties = useState({
            properties: "",
            path: "",
            type: "",
            addButtonBox: "",

        });
        this.ButtonDetails = useState({
            name: "",
            type: "",
            path: "",
            position: "",
            class_name: "",
            string: "",

        })
        this.ActivityDetails = useState({
            archInfo: "",
            fields: "",
            activityResIds: "",
            records: "",
        })
        this.handleFormDetails = this.handleFormDetails.bind(this);
        this.handleListDetails = this.handleListDetails.bind(this);
        this.handlePivotDetails = this.handlePivotDetails.bind(this);
        this.handleKanbanDetails = this.handleKanbanDetails.bind(this);
        this.handleKanbanFieldsDetails = this.handleKanbanFieldsDetails.bind(this);
        this.handleCalendarDetails = this.handleCalendarDetails.bind(this);
        this.handleGraphDetails = this.handleGraphDetails.bind(this);
        this.handleKanbanComponent = this.handleKanbanComponent.bind(this);
        this.handleActivityDetails = this.handleActivityDetails.bind(this);
        this.handleButtonInfo = this.handleButtonInfo.bind(this);
        this.handleClearMenu = this.handleClearMenu.bind(this);
        this.handleAsideMenu = this.handleAsideMenu.bind(this);
        this.handleNotebookDetails = this.handleNotebookDetails.bind(this);
        this.handleSmartButtonDetails = this.handleSmartButtonDetails.bind(this);
        this.reload = this.reload.bind(this);

        useBus(this.env.bus, 'CLEAR-MENU', this.handleClearMenu.bind(this));
        useBus(this.env.bus, 'ASIDE-MENU', this.handleAsideMenu.bind(this));
        useBus(this.env.bus, 'KANBAN_COMPONENT', this.handleKanbanComponent.bind(this));
        useBus(this.env.bus, "BUTTON_INFO", this.handleButtonInfo);
        useBus(this.env.bus, "PIVOT_DETAILS", this.handlePivotDetails);
        useBus(this.env.bus, "LIST_DETAILS", this.handleListDetails);
        useBus(this.env.bus, "ACTIVITY_DETAILS", this.handleActivityDetails);
        useBus(this.env.bus, "SELECT_NOTEBOOK", this.handleNotebookDetails);
        useBus(this.env.bus, "RENDER_LOAD", this.reload);

        useBus(this.env.bus, "FORM_DETAILS", this.handleFormDetails);
        useBus(this.env.bus, "SMART_BUTTON_DETAILS", this.handleSmartButtonDetails);

        useBus(this.env.bus, "KANBAN_DETAILS", this.handleKanbanDetails);
        useBus(this.env.bus, "KANBAN_FIELD_DETAILS", this.handleKanbanFieldsDetails);
        useBus(this.env.bus, "CALENDAR_DETAILS", this.handleCalendarDetails);
        useBus(this.env.bus, "GRAPH_DETAILS", this.handleGraphDetails);

        this.handleFieldDetails = this.handleFieldDetails.bind(this);
        this.handleButtonDetails = this.handleButtonDetails.bind(this);
        this.handleExistingField = this.handleExistingFieldDetails.bind(this);

        useBus(this.env.bus, "FIELDS_DETAILS", this.handleFieldDetails);
        useBus(this.env.bus, "BUTTON_DETAILS", this.handleButtonDetails);
        useBus(this.env.bus, "LIST_EXISTING_FIELDS", this.handleExistingField);
        console.log("StdWrppr", this)

    }
    updateViewDetails(detail) {
        if (detail) {
            Object.assign(this.viewDetails, {
                model: detail.model ?? this.viewDetails.model,
                viewId: detail.viewId ?? this.viewDetails.viewId,
                viewType: detail.viewType ?? this.viewDetails.viewType,
                type: detail.type ?? this.viewDetails.type,
                allFields: (detail.allFields ?? this.viewDetails.allFields) || {}
            });
        }
    }

    reload(){
        this.action.doAction("studio_reload");
        setTimeout(() => {
            this.props.updateState("edit", true);
            },100)
    }

    handleExistingFieldDetails() {
        this.dialogService.add(ExistingFieldDialog, {
            fields: this.overall.allFields,
            model: this.viewDetails.model,
            viewType: this.viewDetails.viewType,
            viewId: this.viewDetails.viewId,
        });
    }
    handleView(ev) {
        this.viewDetails.type = ev.target.innerText;
    }
    handleFormDetails({
        detail
    }) {
         if (detail) {
            Object.assign(this.overall, {
                mode: detail.mode,
                allFields: detail.allFields,
                activeFields: detail.activeFields,
            });
            this.updateViewDetails(detail);
        }
    }
    handleButtonDetails({
        detail
    }) {
         if (detail) {
            Object.assign(this.ButtonDetails, {
                name: detail.name || "",
                function_type: detail.function_type || "",
                function_name: detail.function_name || "",
                path: detail.path || "",
                newHeader: detail.newHeader || false,
                newButton: detail.newButton || false,
                position: detail.position || "",
                class_name: detail.class || "",
                string: detail?.string || "",
                groupIds: detail?.groupIds || "",
                icon: detail?.icon || '',
                invisible: detail.invisible || '',
                element: detail.element || '',

            });
            this.updateViewDetails(detail);
        }
    }
    handleListDetails({
        detail
    }) {
        if (detail) {
            Object.assign(this.overall, {
                mode: detail.mode,
                allFields: detail.allFields,
                activeFields: detail.activeFields,
            });
            this.updateViewDetails(detail);
        }
    }
    handleActivityDetails({
        detail
    }) {
        if (detail) {
            this.state.activity_view = true
            Object.assign(this.ActivityDetails, {
                archInfo: detail.archInfo,
                fields: detail.fields,
                activityResIds: detail.activityResIds,
                records: detail.records,
                model: detail.model,
                viewId: detail.viewId,
                viewType: detail.viewType,
            });
            this.updateViewDetails(detail);
        } else {
            this.state.activity_view = false
        }
    }
    handleGraphDetails({
        detail
    }) {
        if (detail) {
            Object.assign(this.overall, {
                mode: detail.mode,
                allFields: detail.allFields,
                MetaData: detail.envModel,
            });
            this.updateViewDetails(detail);
        }
    }
    async handleFieldDetails({
        detail
    }) {
        if (detail) {
            Object.assign(this.fieldProperties, {
                attr: detail.mode,
                name: detail.name,
                string: detail.label,
                widget: detail.widget,
                options: detail.options,
                fieldType: detail.fieldType,
                context: detail.context,
                related_model: detail.related_model,
                edit: detail.edit || false,
                path: detail.cy_path || "",
                help: detail.help,
                placeholder: detail.placeholder || "",
                invisible: detail.invisible,
                readonly: detail.readonly,
                required: detail.required,
                create: detail.create,
                field_path: detail.field_path || "",
                domain: detail.domain || ""
            });
            this.updateViewDetails(detail);
        }
    }

    handleKanbanDetails({
        detail
    }) {
        if (detail) {
            Object.assign(this.overall, {
                allFields: detail.allFields,
                mode: detail.attributes,
                isMenu: detail.isMenu,
                progressAttributes: detail.progressAttributes,
                ribbonElement: detail.ribbonElement,
            });
            this.updateViewDetails(detail);
        }
    }

    handleKanbanFieldsDetails({
        detail
    }) {
        console.log("HndlKnbnFildDtls", detail)
        if (detail) {
            Object.assign(this.overall, {
                activeFields: detail.active_fields,
                allFields: detail.allfields,
                mode: detail.attributes,
                isMenu: detail.isMenu,
                progressAttributes: detail.progressAttributes,
                ribbonElement: detail.ribbonElement,
            });
            Object.assign(this.fieldProperties, {
                attr: detail.mode,
                name: detail.name,
                string: detail.label,
                widget: detail.widget,
                options: detail.options,
                fieldType: detail.fieldType,
                context: detail.context,
                related_model: detail.related_model,
                edit: detail.edit || false,
                path: detail.path || "",
                help: detail.help,
                placeholder: detail.placeholder || "",
                invisible: detail.invisible,
                readonly: detail.readonly,
                required: detail.required,
                create: detail.create,
                field_path: detail.field_path || "",
                domain: detail.domain || ""
            });
            this.updateViewDetails(detail);
        }
    }



    handleCalendarDetails({
        detail
    }) {
        if (detail) {
            Object.assign(this.overall, {
                mode: detail.mode,
                model: detail.model,
                activeFields: detail.activeFields,
                model: detail.model,
                calendar_info: detail.calendar_info
            });
            this.updateViewDetails(detail);
        }
    }
    handlePivotDetails({
        detail
    }) {

        if (detail) {
            Object.assign(this.overall, {
                activeFields: detail.active_fields,
                measure: detail.measure,
                mode: detail.metaData,
                envModel: detail.envModel,
            });
            this.updateViewDetails(detail);
        }
    }
    handleKanbanComponent({
        detail
    }) {
        if (detail) {
            Object.assign(this.kanbanComponent, {
                properties: detail.properties,
                type: detail.type,
                element: detail.element,

            });
            this.updateViewDetails(detail);
        }
    }
    handleSmartButtonDetails({ detail }) {
         if (detail) {
            Object.assign(this.SmartButtonProperties, {
                properties: detail.properties,
                path: detail.path,
                type: detail.type,
                addButtonBox: detail.addButtonBox,
                new_button: detail.new_button,

            });
            this.updateViewDetails(detail);
        }
    }
    handleButtonInfo({
        detail
    }) {
        if (detail) {
            Object.assign(this.buttonInfo, {
                newViewId: detail.newViewId,
                envModel: detail.envModel,
                newHeader: detail.newHeader,
                path: detail.path,
            });
            this.updateViewDetails(detail);
        }
    }
    handleAsideMenu() {
        this.viewDetails.type = 'View'
    }
    handleClearMenu(params) {
        this.props.updateState("editButton", true);
        this.props.edit = false;
        this.viewDetails.type = '';
        if (params?.detail?.fromClose) {
            this.state.isAnimatingSidebar = true;
            setTimeout(() => {
                this.state.isAnimatingSidebar = false;
            }, 800);
        }
        this.action.doAction('studio_reload')
        this.env.bus.trigger('REMOVE_BUTTON_PROPERTIES');
    }
    handleNotebookDetails({
        detail
    }) {

        if (detail) {
            Object.assign(this.noteBookProperties, {
                properties: detail.properties,
                type: detail.type,

            });
            this.updateViewDetails(detail);
        }
    }
    get asideProps() {
        console.log("AsideProps", this)
         return {
            overall: this.overall,
            viewDetails: this.viewDetails,
            fieldProperties: this.fieldProperties,
            kanbanComponent: this.kanbanComponent,
            noteBookProperties: this.noteBookProperties,
            SmartButtonProperties: this.SmartButtonProperties,
            ButtonDetails: this.ButtonDetails,
            type: this.viewDetails.type || (this.props.edit ? "View" : ""),
            handleView: this.handleView.bind(this),
            isAnimatingSidebar: this.state?.isAnimatingSidebar,
            activity_view: this.state?.activity_view,
            updateState: this.props.updateState
        };
    }
    get asideBarAvailable() {
        console.log("AsideBarAvlbl", this)
        return this.props.edit || this.viewDetails.type;
    }
    get activityProps() {
        return {
            ...this.ActivityDetails,
            updateState: this.props.updateState,
        }
    }
}
StudioWrapper.components = {
//    MenuSideBar,
    AsideBar,
    MainComponentsContainer,
    ActivityDialog,
    StudioMenuSideBar,
};