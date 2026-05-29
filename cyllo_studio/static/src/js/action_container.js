/** @odoo-module **/
import { ActionContainer } from "@web/webclient/actions/action_container";
import { AsideBar } from "@cyllo_studio/js/view_editor/aside_bar/aside_bar";
import { patch } from "@web/core/utils/patch";
import { StudioWrapper } from "@cyllo_studio/js/root/studio_wrapper";
import { useEffect } from "@odoo/owl";

patch(ActionContainer.prototype, {
  setup() {
    super.setup();
    useEffect(
      () => {
        const { action } = this.info?.componentProps || {};
        if (action) {
          this.props.updateState("editButton", false);
          this.props.updateState("edit", false);
          this.props.updateState("view", false);
        } else {
          this.props.updateState("editButton", true);
          this.props.updateState("view", true);
        }
      },
      () => [this.info?.componentProps]
    );
  },
  get wrapperProps() {
    return {
      info: this.info,
      edit: this.props.edit,
      viewChanged: this.props.viewChanged,
      updateState: this.props.updateState,
    };
  },
});
ActionContainer.template = "cyllo_studio.ActionContainer";
ActionContainer.props = {
  edit: { type: Boolean, optional: true },
  view: { type: Boolean, optional: true },
  editButton: { type: Boolean, optional: true },
  viewChanged: { type: Boolean, optional: true },
  updateState: { type: Function, optional: true },
  isAnimatingSidebar: { type: Boolean, optional: true },
  activity_view: { type: Boolean, optional: true },
   viewDetails: { type: Object, optional: true },


};
ActionContainer.components = {
  ...ActionContainer.components,
  AsideBar,
  StudioWrapper,
};
