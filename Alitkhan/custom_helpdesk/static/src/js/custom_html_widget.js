
import { HtmlField, htmlField } from "@html_editor/fields/html_field";
import { TextField, textField } from "@web/views/fields/text/text_field";

import { registry } from "@web/core/registry";

export class CustomHtmlField extends HtmlField {
    static template = "custom_helpdesk.HtmlField"
    setup() {
        super.setup();
    }
    stripHtml(value) {
        if (!value) return '';
        const div = document.createElement("div");
        div.innerHTML = value;
        return div.textContent.trim();
    }

}

export const CustomHtmlFieldData = {
    ...textField,
    ...htmlField,
    component: CustomHtmlField,
};

registry.category("fields").add("custom_html_widget", CustomHtmlFieldData);
