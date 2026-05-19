/** @odoo-module **/

import { FormRenderer } from "@web/views/form/form_renderer";
const { onMounted } = owl;
import { StatusBar } from "@cyllo_studio/js/views/cyllo_form/status_bar/statusbar";
import { ChatterComponent } from "@cyllo_studio/js/views/cyllo_form/chatter/chatter_component";
import { StatusBarButtons } from '@web/views/form/status_bar_buttons/status_bar_buttons';
import { CylloInnerGroup } from "@cyllo_studio/js/views/cyllo_form/form_group/form_group";
import { CylloField } from "@cyllo_studio/js/view_editor/fields/field";
import { CylloNotebook } from "@cyllo_studio/js/views/cyllo_form/notebook/notebook";
import {ButtonBox} from "@web/views/form/button_box/button_box";
import {AvatarComponent} from "@cyllo_studio/js/views/cyllo_form/avatar/avatar";
import { CylloFormLabel } from "@cyllo_studio/js/views/cyllo_form/form_label/form_label";



export class CylloFormRenderer extends FormRenderer {
  setup() {
    super.setup();

    onMounted(() => {
      this.env.bus.trigger("FORM_DETAILS", {
        mode: this.props.archInfo.activeActions,
        model: this.env.model.config.resModel,
        viewId: this.env.config.viewId,
        allFields: this.env.model.config.fields,
        activeFields: this.env.model.config.activeFields,
        viewType: "form",
      });
    });
  }
  handleSelectButton(el){
    console.log("sadasdasdsad",el)
  }
}

CylloFormRenderer.components = {
    ...FormRenderer.components,
    StatusBar:StatusBar,
    ChatterComponent,
    StatusBarButtons,
    AvatarComponent,
    ButtonBox,
    InnerGroup: CylloInnerGroup,
    Field: CylloField,
    Notebook:CylloNotebook,
    FormLabel: CylloFormLabel,


};