/** @odoo-module **/
import { formView } from "@web/views/form/form_view";
import { registry } from "@web/core/registry";
import { CylloFormRenderer } from "./cyllo_form_renderer";
import {CylloFormCompiler} from "./view_compiler";
import {CylloFormController} from "./cyllo_form_controller";


export const CylloFormView = {
    ...formView,
    Renderer: CylloFormRenderer,
    Compiler: CylloFormCompiler,
    Controller: CylloFormController,

};

registry.category("views").add("form", CylloFormView, { force: true });
