/** @odoo-module **/
import { onMounted } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { StudioWrapperMain } from "@cyllo_studio/js/root/studio_wrapper_main";

patch(WebClient.prototype, {
  setup() {
    super.setup();
    onMounted(() => {
      const darkMode = localStorage.getItem("lightModeStudio");
      if (darkMode) {
        document.body.classList.add("light-studio-mode");
      }
    });
  },
});
WebClient.template = "cyllo_studio.WebClient";
WebClient.components = {
  ...WebClient.components,
  StudioWrapperMain,
};
