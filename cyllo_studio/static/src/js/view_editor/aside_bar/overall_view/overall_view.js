/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { ListOverall } from "@cyllo_studio/js/views/cyllo_list/list_overall";
import { FormOverall } from "@cyllo_studio/js/views/cyllo_form/form_overall";
import { PivotOverall } from "@cyllo_studio/js/views/cyllo_pivot/pivot_overall";
import { _t } from "@web/core/l10n/translation";
import { KanbanOverall } from "@cyllo_studio/js/views/cyllo_kanban/kanban_overall";
import { CalendarOverall } from "@cyllo_studio/js/views/cyllo_calendar/calendar_overall";
import { GraphOverall } from "@cyllo_studio/js/views/cyllo_graph/graph_overall";

export class OverallView extends Component {
  static template = "cyllo_studio.OverallView";
  static props = {
    mode: { type: Object, optional: true },
    allFields: { type: Object, optional: true },
    activeFields: { type: Object, optional: true },
    viewType: { type: String, optional: true },
    model: { type: String, optional: true },
    calendar_info: { type: Object, optional: true },
    viewId: { type: Number, optional: true },
    edit: { type: Boolean, optional: true },
    isMenu: { type: Boolean, optional: true },
    progressAttributes: { type: Object, optional: true },
    ribbonElement: { type: NodeList, optional: true },
    measure: { type: Object, optional: true },
    envModel: { type: Object, optional: true },
    type: { type: String, optional: true },
    MetaData:{ type: Object, optional: true },

  };
  setup() {
    this.rpc = useService("rpc");
    this.notification = useService("effect");
    this.actionService = useService("action");
    this.state = useState({
      viewType: "",
    });
  }
  showInvisibleFields(ev){
        if(ev.target.checked){
            sessionStorage.setItem('invisible', this.state.invisible);
            window.location.reload()
        }else{
            sessionStorage.removeItem('invisible');
            window.location.reload()
        }
  }
  get commonProps() {
    return {
      envModel:this.props.envModel,
      mode: this.props.mode,
      viewType: this.props.viewType,
      model: this.props.model,
      viewId: this.props.viewId,
      handleView: this.handleView.bind(this),
      showInvisibleFields: this.showInvisibleFields.bind(this),
    };
  }
  get overallListProps() {
    return {
      ...this.commonProps,
      allFields: this.props.allFields,
      activeFields: this.props.activeFields,
    };
  }
  get overallPivotProps() {
    return {
      ...this.commonProps,
      activeFields: this.props.activeFields,
    };
  }
  get overallCalendarProps() {
    return {
      ...this.commonProps,
      activeFields: this.props.activeFields,
      model :this.props.calendar_info,
         };
  }
  get overallFormProps() {
    return {
      ...this.commonProps,
      allFields: this.props.allFields,
      activeFields: this.props.activeFields,
    };
  }
  get overallGraphProps() {
    return {
      ...this.commonProps,
      allFields: this.props.allFields,
      MetaData:this.props.MetaData,

    };
  }
  get overallKanbanProps() {
    return {
      ...this.commonProps,
      allFields: this.props.allFields,
      isMenu: this.props.isMenu,
      progressAttributes: this.props.progressAttributes,
      ribbonElement: this.props.ribbonElement,
    };
  }

  async handleView(name, value = null, order = null) {
    if (name) {
      try {
        await this.rpc("cyllo_studio/edit/overall_view", {
          method: "edit_overallView",
          args: [
            {
              model: this.props.model,
              view_type: this.props.viewType,
              view_id: this.props.viewId,
            },
          ],
          kwargs: {
            value: value,
            attr: name,
            path: '/' + this.props.viewType,
            order: order,
          },
        });
      } finally {
        this.notification.add({
          title: _t("Success"),
          message: "Changes Added.",
          description: "Exit Studio Mode To View Changes",
          type: "notification_panel",
          notificationType: "success",
          animation: false,
        });
      }
    }
    this.actionService.doAction("view_reload");
  }
}
OverallView.components = {
  ListOverall,
  FormOverall,
  PivotOverall,
  KanbanOverall,
  CalendarOverall,
  GraphOverall,
};
