/** @odoo-module **/

import { registry } from "@web/core/registry";

export const clipboardService = {
    start() {
        function copyTextToClipboard(text) {
            navigator.clipboard.writeText(text).catch(err => {
                console.error('Copy failed', err);
            });
        }

        const copyElements = document.querySelectorAll(".dx_auto_offering_copy-on-click");
        
        copyElements.forEach((element, index) => {
            element.addEventListener("click", () => {
                console.log(element.innerHTML);
                copyTextToClipboard(element.innerHTML);
            });
        });
    }
};

registry.category('services').add('clipboard_service', clipboardService);
