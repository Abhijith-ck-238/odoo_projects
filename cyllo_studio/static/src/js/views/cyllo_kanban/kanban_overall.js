/** @odoo-module **/
import { Component } from "@odoo/owl";
import { _t } from "@web/core/l10n/translation";
import { sortBy } from "@web/core/utils/arrays";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import { validateField } from "@cyllo_studio/js/actions/utils";
import { RibbonDialog } from "@cyllo_studio/js/view_editor/kanban/ribbon_dialog";
import { useService } from "@web/core/utils/hooks";



export class KanbanOverall extends Component {
  static template = "cyllo_studio.KanbanOverall";
  setup() {
    this.dialogService = useService("dialog");
    console.log("asdasdasdasdasdadasd", this);
  }
  get kanbanFields() {
    const fields = [];
    for (const [fieldName, field] of Object.entries(this.props.allFields)) {
      if (validateField(fieldName, field)) {
        fields.push({ value: fieldName, label: field.string });
      }
    }
    return [["", ""], ...sortBy(fields, "label")];
  }
//  handleKanbanView(name, value) {
//    console.log("asdasdsadsadadsas", name, value);
//  }
      editRibbon(){
         this.dialogService.add(RibbonDialog,{
//            fields: this.props.kanbanInfo.fields,
            ribbonElement: this.props.ribbonElement,
            viewDetails: {
                viewId: this.props.viewId,
                viewType: this.props.viewType,
                model: this.props.model,
                active_fields:this.props.allFields,
            },
        })
    }


}
KanbanOverall.components = {
  CylloStudioDropdown,
};
