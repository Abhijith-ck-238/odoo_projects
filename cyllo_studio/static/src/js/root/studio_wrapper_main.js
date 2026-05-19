/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { CylloNavBar } from "@cyllo_studio/js/navbar/navbar";
import { ActionContainer } from "@web/webclient/actions/action_container";
import { MainComponentsContainer } from "@web/core/main_components_container";

export class StudioWrapperMain extends Component {
  static template = "cyllo_studio.StudioWrapperMain";
  setup() {
    this.state = useState({
      edit: false,
      viewChanged: false,
      editButton: true,
      view: true,
      viewDetails:{}
//      isAnimatingSidebar: false,
    });
    this.updateState = this.updateState.bind(this);
  }
  updateState(attr, value) {
    this.state[attr] = value;
  }
  get viewProps() {
    return { ...this.state, updateState: this.updateState };
  }
}
StudioWrapperMain.components = {
  CylloNavBar,
  MainComponentsContainer,
  ActionContainer,
};
