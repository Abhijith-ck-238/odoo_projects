/** @odoo-module **/
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { onMounted } from "@odoo/owl";
import { KANBAN_MENU_ATTRIBUTE } from "@web/views/kanban/kanban_arch_parser";
import { CylloKanbanRecord } from "./cyllo_kanban_record";
import { KanbanComponents } from "./kanban_components";


import { _t } from "@web/core/l10n/translation";
export class CylloKanbanRenderer extends KanbanRenderer {
  setup() {
    super.setup();
    onMounted(() => {
      const ribbonElement = document.querySelectorAll('[data-ribbon="1"]');
      this.env.bus.trigger("KANBAN_DETAILS", {
        viewType: this.env.config.viewType,
        model: this.props.list._config.resModel,
        viewId: this.env.config.viewId,
        allFields: this.props.list.model.config.fields,
        isMenu: KANBAN_MENU_ATTRIBUTE in this.props.archInfo.templateDocs,
        progressAttributes: this.props.archInfo.progressAttributes || {},
        ribbonElement: ribbonElement,
        attributes: {
          create: this.props.archInfo.activeActions.create,
          quickCreate: this.props.archInfo.activeActions.quickCreate,
          defaultGroupBy: this.props.archInfo.defaultGroupBy,
          recordsDraggable: this.props.archInfo.recordsDraggable,
          groupsDraggable: this.props.archInfo.groupsDraggable,
        },
      });
    });
  }
  getGroupsOrRecords() {
        const { list } = this.props;
         if (list.isGrouped) {
        const validGroup = [...list.groups].map((group, i) => ({
            group,
//            key: isNull(group.value) ? `group_key_${i}` : String(group.value),
        })).find(item => item.group.records && item.group.records.length > 0);
        if (validGroup) {
            return validGroup;
        }
        } else {
            return list.records.map((record) => ({ record, key: record.id }))[0];
        }
    }

}

CylloKanbanRenderer.components = {
    ...KanbanRenderer.components,
    CylloKanbanRecord,
    KanbanComponents,
 }
CylloKanbanRenderer.template = "cyllo_studio.CylloKanbanRenderer"
