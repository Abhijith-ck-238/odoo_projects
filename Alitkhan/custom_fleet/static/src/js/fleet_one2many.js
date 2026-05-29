import {Component, onWillStart, useRef} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { registry } from "@web/core/registry";
import { _t } from "@web/core/l10n/translation";
import { useTagNavigation } from "@web/core/record_selectors/tag_navigation_hook";


export class FleetOne2Many extends Component {
    static template = "custom_fleet.FleetOne2Many";
    // static props = {
    //     ids: { type: Array, optional: true },
    // };
    // static defaultProps = {
    //     canCreate: true,
    //     canQuickCreate: true,
    //     canCreateEdit: true,
    //     nameCreateField: "name",
    //     context: {},
    // };


    setup() {
        this.orm = useService("orm");
        this.previousColorsMap = {};
        // this.popover = usePopover(this.constructor.components.Popover);
        this.dialog = useService("dialog");
        this.dialogClose = [];

        onWillStart(async () => {
            this.record = await this.orm.searchRead(
                "service.intervals",
                [["id", "in", this.props.record.data[this.props.name].resIds]],
                [],
                {}
            );
            console.log(this.record,'this.recordthis.record')
        });

        // this.records = this.pyEnv["service.intervals"].search_read([
        //         ["id", "in", this.props.record.data[this.props.name].resIds],
        //     ]);
        // console.log(this.records,'this.recordsthis.records')
        // this.onTagKeydown = useTagNavigation(
        //     "many2ManyTagsField",
        //     this.deleteTagByIndex.bind(this)
        // );
        // // this.autoCompleteRef = useRef("autoComplete");
        // const { saveRecord, removeRecord } = useX2ManyCrud(
        //     () => this.props.record.data[this.props.name],
        //     true
        // );

        // this.activeActions = useActiveActions({
        //     fieldType: "many2many",
        //     crudOptions: {
        //         create: this.props.canCreate && this.props.createDomain,
        //         createEdit: this.props.canCreateEdit,
        //         onDelete: removeRecord,
        //         edit: this.props.record.isInEdition,
        //     },
        //     getEvalParams: (props) => {
        //         return {
        //             evalContext: this.evalContext,
        //             readonly: props.readonly,
        //         };
        //     },
        // });
        //
        // this.openMany2xRecord = useOpenMany2XRecord({
        //     resModel: this.relation,
        //     activeActions: {
        //         create: false,
        //         write: true,
        //     },
        //     onRecordSaved: async (record) => {
        //         await this.props.record.data[this.props.name].forget(record);
        //         return saveRecord([record.resId]);
        //     },
        // });
        //
        // this.update = (recordlist) => {
        //     recordlist = recordlist
        //         ? recordlist.filter((element) => {
        //               return !this.tags.some((record) => record.resId === element.id);
        //           })
        //         : [];
        //     if (!recordlist.length) {
        //         return;
        //     }
        //     const resIds = recordlist.map((rec) => rec.id);
        //     return saveRecord(resIds);
        // };
        //
        // if (this.props.canQuickCreate) {
        //     this.quickCreate = async (name) => {
        //         const created = await this.orm.call(this.relation, "name_create", [name], {
        //             context: this.props.context,
        //         });
        //         return saveRecord([created[0]]);
        //     };
        // }
    }

    // get relation() {
    //     return this.props.record.fields[this.props.name].relation;
    // }
    // get evalContext() {
    //     return this.props.record.evalContext;
    // }
    // get string() {
    //     return this.props.string || this.props.record.fields[this.props.name].string || "";
    // }
    //
    // getTagProps(record) {
    //     return {
    //         id: record.id, // datapoint_X
    //         resId: record.resId,
    //         text: record.data.display_name,
    //         colorIndex: record.data[this.props.colorField],
    //         canEdit: this.props.canEditTags,
    //         onDelete: !this.props.readonly ? () => this.deleteTag(record.id) : undefined,
    //         onKeydown: (ev) => {
    //             if (this.props.readonly) {
    //                 return;
    //             }
    //             this.onTagKeydown(ev);
    //         },
    //     };
    // }
    //
    // get tags() {
    //     return this.props.record.data[this.props.name].records.map((record) =>
    //         this.getTagProps(record)
    //     );
    // }
    //
    // get showM2OSelectionField() {
    //     return !this.props.readonly;
    // }
    //
    // async deleteTagByIndex(index) {
    //     const { id } = this.tags[index] || {};
    //     this.deleteTag(id);
    // }
    //
    // async deleteTag(id) {
    //     const tagRecord = this.props.record.data[this.props.name].records.find(
    //         (record) => record.id === id
    //     );
    //     await this.props.record.data[this.props.name].forget(tagRecord);
    // }
    //
    // getDomain() {
    //     return Domain.and([
    //         getFieldDomain(this.props.record, this.props.name, this.props.domain),
    //     ]).toList(this.props.context);
    // }
    //
    // getOptionClassnames(record) {
    //     const records = this.props.record.data[this.props.name].records;
    //     const isSelected = records.some((r) => r.resId === record.id);
    //     return isSelected ? "dropdown-item-selected" : "";
    // }
}

export const Fleet_one2Many = {
    component: FleetOne2Many,
    displayName: _t("Fleet_one2Many"),
    supportedOptions: [
        {
            label: _t("Disable creation"),
            name: "ids",
            type: "array",
            help: _t(
                "If checked, users won't be able to create records through the autocomplete dropdown at all."
            ),
        },
    ],
    extractProps(data) {
        return data;
    },
};

registry.category("fields").add("Fleet_one2Many", Fleet_one2Many)