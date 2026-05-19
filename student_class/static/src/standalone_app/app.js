/** @odoo-module */
import { whenReady } from "@odoo/owl";
import { mountComponent } from "@web/env";
import { StudentClassDashboard } from "./root";

whenReady(() => mountComponent(StudentClassDashboard, document.body));
