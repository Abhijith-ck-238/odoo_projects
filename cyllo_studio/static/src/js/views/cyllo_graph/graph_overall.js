/** @odoo-module **/
import {
    Component,
    useState,
    onMounted
} from "@odoo/owl";
import {
    useBus,
    useService
} from "@web/core/utils/hooks";
import {
    handleUndoRedo
} from "@cyllo_studio/js/utils/undo_redo_utils";

import {
    CylloStudioDropdown
} from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import {
    validateField
} from "@cyllo_studio/js/actions/utils";
import {
    sortBy
} from "@web/core/utils/arrays";
import {
    DropdownItem
} from "@web/core/dropdown/dropdown_item";
import {
    Dropdown
} from "@web/core/dropdown/dropdown";
import {
    AccordionItem
} from "@web/core/dropdown/accordion_item";
import {
    _t
} from "@web/core/l10n/translation";

export class GraphOverall extends Component {
    static template = "cyllo_studio.GraphOverall";
    setup() {
        console.log("Asfdfdsfsdf", this.props.mode.modes)
        this.action = useService("action");
        this.notification = useService("effect");
        this.rpc = useService("rpc");
        console.log("CptlzFrstLttr22", this.props)
        this.state = useState({
            New: true,
            stacked: this.props.MetaData.metaData.stacked,
            link: this.props.MetaData.metaData.disableLinking ?
                this.props.MetaData.metaData.disableLinking :
                false,
            groupBy: this.props.MetaData.metaData.groupBy,
            fields: [], // Initialize fields in state
            activeGraphs: this.props.mode.modes || [],
            currentPage: 0,
            itemsPerPage: 4,
            currentOrder: this.props.mode.order,
            currentType: this.props.mode.mode


            //      field:filterFieldsByType,
        });

        onMounted(() => {
            const fields = [];
            for (const [fieldName, field] of Object.entries(this.props.allFields)) {
                if (validateField(fieldName, field)) {
                    fields.push(
                        Object.assign({
                                name: fieldName,
                            },
                            field
                        )
                    );
                }
            }
            const sortedFields = sortBy(fields, "string");
            this.state.fields = sortedFields;
        });
    }
    capitalizeFirstLetter(string) {
        console.log("CptlzFrstLttr", string, this)
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    get sortGraph() {
        const values = ["ASC", "DESC"];
        const labels = ["Ascending", "Descending"];
        return values.map((value, index) => ({
            value: value,
            label: labels[index],
        }));
        console.log("qweqeq", value, label)
    }
    get visibleGraphTypes() {
        const totalItems = this.state.activeGraphs.length;
        const startIndex = this.state.currentPage;
        const visibleIcons = [];

        // Loop through the icons and fill the visibleIcons array
        if (totalItems <= 4) {
            this.state.itemsPerPage = totalItems
        }
        console.log("itemsPerPage", this.state.itemsPerPage)
        for (let i = 0; i < this.state.itemsPerPage; i++) {
            console.log("qwqwqwdqwdqdqdqdqd", this.state.activeGraphs)
            const index = (startIndex + i) % totalItems;
            console.log("qwqwqwdqwdqdqdqdwewewqd", index)
            console.log("qwqwqwdqwdqdqdqdwewewqd", totalItems, startIndex)

            visibleIcons.push(this.state.activeGraphs[index]);
        }
        console.log("visibleIcons", visibleIcons)
        return visibleIcons;
    }

    get chartTypes() {
        const types = this.visibleGraphTypes;
        return types.map(type => ({
            value: type,
            label: type.charAt(0).toUpperCase() + type.slice(1)
        }));
    }

    //   filterFieldsByType(fields) {
    //        // Filter fields based on the types specified in `this.groupBy_types`
    //        return Object.entries(fields).reduce((filtered, [fieldName, fieldInfo]) => {
    //            if (this.groupBy_types.includes(fieldInfo.type) && fieldInfo.searchable) {
    //                filtered[fieldName] = fieldInfo;
    //            }
    //            return filtered;
    //        }, {});
    //    },

    get graphIcons() {
        const ICONCLASS = {
            bar: "ri-bar-chart-fill",
            line: "ri-line-chart-line",
            pie: "ri-pie-chart-fill",
            doughnut: "ri-donut-chart-fill",
            scatter: "ri-bubble-chart-line",
            bubble: "ri-bubble-chart-fill",
            polarArea: "ri-pie-chart-line",
            radar: "ri-flow-chart",
        };
        return ICONCLASS;
    }
    onClickGraphIcon(event, type) {
        console.log("Adasdasdasdasdasdasdasda", event.target)
        //        if (this.lastClickedIcon) {
        //            this.lastClickedIcon.classList.remove('active-icon');
        //        }
        //        event.target.classList.add('active-icon');
        //        this.lastClickedIcon = event.target;
        //        const iconType = event.target.getAttribute('data-tooltip');
        //        this.state.graph_type = iconType;
        this.props.MetaData.updateMetaData({
            mode: type
        });
    }
    prevPage() {
        console.log("akkkkkkkkkkkkkkkkkkkkkkkk")
        const totalItems = this.state.activeGraphs.length;
        const maxIndex = totalItems - 1;
        this.state.currentPage = (this.state.currentPage - this.state.itemsPerPage + totalItems) % totalItems;
    }
    nextPage() {
        const totalItems = this.state.activeGraphs.length;
        this.state.currentPage = (this.state.currentPage + this.state.itemsPerPage) % totalItems;
    }



    async updateOrder(value) {
        console.log("asdasdasdasdasdasdasdasdasdasda", this)
        this.state.currentOrder = value;
        this.env.services.ui.block();
        var nextOrder = value
        var name = 'order'
        const item_type = value
        const interval = ""
        //        this.props.envModel?.model?.updateMetaData({
        this.props.MetaData.updateMetaData({
            order: nextOrder
        });
        const position = ["disable_linking", "order"].includes(name) ?
            "attributes" :
            "inside";
        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
            });
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.env.services.ui.unblock();
        }
        this.state.New = true;
    }
    async toggleStacked() {
        this.env.services.ui.block();

        const {
            stacked
        } = this.props.MetaData.metaData;
        this.props.MetaData.updateMetaData({
            stacked: !stacked
        });
        const position = "attributes"
        const item_type = !stacked
        const name = 'stacked'
        const interval = ""
        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
            });
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.env.services.ui.unblock();
        }
        this.state.New = true;

    }

    async updateDefaultType(mode) {
        this.env.services.ui.block();
        console.log('this', this)
        const position = "attributes";
        const item_type = mode;
        const name = "type";
        const interval = "";

        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
            });

        } finally {
            this.env.services.ui.unblock();
        }
        try {
            this.notification.add({
                title: _t("Success"),
                message: "Default Chart Updated",
                description: "Exit Studio Mode To View Changes",
                type: "notification_panel",
                notificationType: "success",
                time: 2000,
            });
        } finally {
            this.action.doAction('studio_reload');
            this.state.currentType = mode;
        }
        this.state.New = true;
    }

    async updateGraph(name, item_type, interval = "") {
        console.log("updateGraph")
        this.env.services.ui.block();
        const position = "attributes";
        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
            });
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.env.services.ui.unblock();
        }
        try {
            this.notification.add({
                title: _t("Success"),
                message: "Changes Added.",
                description: "Exit Studio Mode To View Changes",
                type: "notification_panel",
                notificationType: "success",
                time: 1000,
            });
        } finally {
            this.action.doAction('studio_reload');
        }
        this.state.New = true;
    }
    async updateDimension(name, item_type = false, interval = "") {
        this.env.services.ui.block();

        const position = "inside"
        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
            });
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.env.services.ui.unblock();
        }
        this.action.doAction("studio_reload");
        this.state.New = true;
    }
    async updateDimensions(field) {
        const position = "inside";
        const item_type = false
        //        const prevValue = this.prevValues.Dimension[0]
        const name = field
        const interval = ""
        this.env.services.ui.block();
        try {
            const response = await this.rpc("cyllo_studio/graph/edit_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                position,
                name,
                item_type,
                interval,
                //                prevValue
            });
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.notification.add({
                title: _t("Success"),
                message: "Changes Added.",
                description: "Exit Studio Mode To View Changes",
                type: "notification_panel",
                notificationType: "success",
            });
            this.env.services.ui.unblock();
        }
        window.location.reload();
        this.state.New = true;

    }
    async removeGroupBy(measure, field) {
        const path = this.props.model;
        if (!field) {
            this.state.New = true;
            return;
        }
        this.env.services.ui.block();
        try {
            const response = await this.rpc("cyllo_studio/graph/remove_element", {
                model: this.props.model,
                view_type: this.props.viewType,
                view_id: this.props.viewId,
                field,

            });
            this.state.group_by = this.state.groupBy.filter(item => item !== field)
            //             if(response){
            //                    this.handleUndoRedo(response)
            //                }
        } finally {
            this.env.services.ui.unblock();
        }
        window.location.reload();
        this.state.New = true;
    }



    handleGroupBy() {
        this.state.New = false;
    }
}
GraphOverall.components = {
    CylloStudioDropdown,
    Dropdown,
    DropdownItem,
    AccordionItem,
};