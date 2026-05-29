/** @odoo-module */

import { Component, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { KanbanRecord } from "@web/views/kanban/kanban_record";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { patch } from "@web/core/utils/patch";

// Generic One2ManyTree Component
export class One2ManyTree extends Component {
    static template = "web_one2many_kanban.One2ManyTree";

    setup() {
        this.orm = useService("orm");

        onWillStart(async () => {
            const fieldInfo = this.props.record.fields[this.props.name];
            const relatedModel = fieldInfo.relation;

            this.records = await this.orm.searchRead(
                relatedModel,
                [["id", "in", this.props.record.data[this.props.name].resIds || []]],
                [],
                {}
            );

            const fields = await this.orm.call(relatedModel, "fields_get", []);
            this.displayColumns = Object.entries(fields)
                .filter(([name, field]) => field.type !== "one2many" && field.type !== "many2many")
                .map(([name, field]) => ({
                    name,
                    label: field.string || name,
                }))
                .slice(0, 3); // Limit to 3 columns
        });
    }
}

registry.category("fields").add("one2many_tree", {
    component: One2ManyTree,
    displayName: _t("One2Many Tree"),
    supportedOptions: [],
    extractProps(data) {
        return data;
    },
});

// Define the custom KanbanRecord
export class CustomKanbanRecord extends KanbanRecord {
    static template = "web_one2many_kanban.CustomKanbanRecord";
    static components = { ...KanbanRecord.components, One2ManyTree };
}

// Patch KanbanRenderer
patch(KanbanRenderer.prototype, {
    setup() {
        super.setup(...arguments);

        // Ensure archInfo is initialized
        this.props.archInfo = this.props.archInfo || {};

        // Parse the Kanban arch to find One2Many fields with the one2many_tree widget
        const parser = new DOMParser();
        const archDoc = parser.parseFromString(this.props.arch || "", "text/xml");
        const one2manyFields = Array.from(archDoc.querySelectorAll("field[widget='one2many_tree']"))
            .map((node) => node.getAttribute("name"))
            .filter(Boolean);

        // Set one2manyFields in archInfo
        this.props.archInfo.one2manyFields = one2manyFields;

        // Override the KanbanRecord component
        this.components = { ...this.components, KanbanRecord: CustomKanbanRecord };
    },
});

// Patch KanbanRecord
patch(CustomKanbanRecord.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
        // Ensure one2manyFields is always an array
        this.one2manyFields = (this.props.archInfo && this.props.archInfo.one2manyFields) || [];
    },
});