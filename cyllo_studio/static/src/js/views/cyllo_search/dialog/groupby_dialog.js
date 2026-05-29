/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { Dialog } from "@web/core/dialog/dialog";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import { _t } from "@web/core/l10n/translation";

export class GroupByDialog extends Component {
  static template = "cyllo_studio.GroupByDialog";
  static components = {
    Dialog,
    MultiRecordSelector,
    CylloStudioDropdown,
  };
  setup() {
    this.rpc = useService("rpc");
    this.action = useService("action");
    this.addDialog = useOwnedDialogs();
    this.notification = useService("effect");
    this.state = useState({
      string: "",
      field: null,
      invisible: "false",
      groupIds: [],
    });
    onWillStart(() => {
      if (this.props.properties) {
        this.state.string = this.props.properties.string;
        this.state.field = this.props.properties.field;
        this.state.invisible = this.props.properties.invisible;
        this.state.groupIds = this.props.properties.groupIds;
      }
    });
    console.log(this);
  }

  onDomainRadioClick() {
    this.state.invisible = this.state.invisible === "false" ? "true" : "false";
  }

  // onDomainClick() {
  //   this.addDialog(ExpressionEditorDialog, {
  //     resModel: this.props.model,
  //     fields: this.props.allFields,
  //     expression: this.state.invisible,
  //     onConfirm: (expression) => (this.state.invisible = expression),
  //   });
  // }

  get Fields() {
    const arr = [];
    console.log("kaeqweqweqwku", this.props.fields);
    for (let value in this.props.fields) {
      const obj = {
        value: this.props.fields[value].name,
        label: this.props.fields[value].string,
      };
      arr.push(obj);
    }
    console.log("kaeqweqweqwku", arr);

    return arr;
  }

  get defaultFields() {
    return this.state.field;
  }

  handleFieldSelect(value) {
    this.state.field = value;
  }

  async onConfirm() {
    if (!this.state.field) {
      this.notification.add({
        title: _t("Warning"),
        message: "Please select a field.",
        type: "notification_panel",
        notificationType: "warning",
      });
      return;
    }

    let rpcUrl = "cyllo_studio/add/group_by";

    let properties = {
      string: this.state.string,
      field: this.state.field,
      invisible: this.state.invisible,
      groupIds: this.state.groupIds,
    };

    if (this.props.properties) {
      rpcUrl = "cyllo_studio/update/group_by";
      properties = Object.keys(properties).reduce((acc, key) => {
        if (properties[key] != this.props.properties[key]) {
          acc[key] = properties[key];
        }
        return acc;
      }, {});
      if ("field" in properties) {
        properties.context = {
          group_by: properties.field,
        };
        delete properties.field;
      }
    }
    this.env.services.ui.block();
    try {
      const response = await this.rpc(rpcUrl, {
        path: this.props.path,
        view_id: this.props.viewId,
        model: this.props.model,
        properties,
      });
      if (response) {
        let storedArray = JSON.parse(sessionStorage.getItem("UndoRedo")) || [];
        let cleanedStr = response.replace(/\s+/g, " ").trim();
        storedArray.push(cleanedStr);
        sessionStorage.setItem("UndoRedo", JSON.stringify(storedArray));
        sessionStorage.setItem("ReDO", JSON.stringify([]));
      }
    } finally {
      this.env.services.ui.unblock();
    }
//    this.action.doAction("studio_reload");
        window.location.reload()
    this.props.close();
  }
  onDiscard() {
    this.props.close();
  }
}
