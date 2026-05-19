/** @odoo-module **/
import { Systray } from "@cyllo_web/js/systray/cyllo_systray/systray";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(Systray.prototype, {
  async _onClick() {
    const currentUrl = new URL(window.location.href);
    const urlParams = currentUrl.searchParams;
    urlParams.delete("studio");
    urlParams.set("studio", "1");
    window.location.href = currentUrl.toString();
  },
});

