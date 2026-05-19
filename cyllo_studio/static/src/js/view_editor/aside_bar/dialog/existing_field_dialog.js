/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

const fieldIcons = [
  { fieldType: "integer", icon: "ri-numbers-line" },
  { fieldType: "char", icon: "ri-text" },
  { fieldType: "many2one", icon: "ri-link" },
  { fieldType: "many2many", icon: "ri-links-line" },
  { fieldType: "one2many", icon: "ri-share-box-line" },
  { fieldType: "text", icon: "ri-file-text-line" },
  { fieldType: "selection", icon: "ri-arrow-down-s-line" },
  { fieldType: "boolean", icon: "ri-checkbox-line" },
  { fieldType: "binary", icon: "ri-file-binary-line" },
  { fieldType: "datetime", icon: "ri-calendar-line" },
  { fieldType: "date", icon: "ri-calendar-event-line" },
  { fieldType: "html", icon: "ri-code-line" },
  { fieldType: "float", icon: "ri-compass-line" },
  { fieldType: "monetary", icon: "ri-money-dollar-circle-line" },
];

export class ExistingFieldDialog extends Component {
  static template = "cyllo_studio.ExistingFieldDialog";
  setup() {
    this.rpc = useService("rpc");
    this.notification = useService("effect");
    this.action = useService("action");

    this.state = useState({
      fields: [],
    });
    onWillStart(() => {
      Object.keys(this.props.fields).forEach((key) => {
        const field = this.props.fields[key];

        const matchedIcon = fieldIcons.find(
          (icon) => icon.fieldType === field.type
        );

        if (matchedIcon) {
          if (!field.icon) {
            field.icon = matchedIcon.icon;
          }
          if (!field.iconName) {
            field.iconName = matchedIcon.fieldType;
          }
        }
      });
    });
  }
  existingField(ev, item) {
    this.state.fields.push(item);
  }
  async onConfirm() {
    console.log("dsadsadd", this);
    try {
      await this.rpc("cyllo_studio/add/existing_field", {
        method: "add_existing_field",
        args: [
          {
            model: this.props.model,
            view_type: this.props.view_type,
            view_id: this.props.viewId,
            path: "/tree",
            position: "inside",
          },
        ],
        kwargs: {
          value: this.state.fields,
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
      this.action.doAction("view_reload");
    }
  }
}
ExistingFieldDialog.components = {
  Dialog,
  CylloStudioDropdown,
};
