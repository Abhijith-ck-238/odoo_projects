/** @odoo-module */
import { Component, onWillStart, useState } from "@odoo/owl";

export class StudentClassDashboard extends Component {
    setup() {
        this.state = useState({
            students: [],
        });
        onWillStart(async () => {
            if (odoo.students) {
                this.state.students = odoo.students;
            }
        });
    }
    getStateColor(state) {
        switch (state) {
            case "draft":
                return "bg-secondary";
            case "confirmed":
                return "bg-primary";
            case "done":
                return "bg-success";
            default:
                return "bg-light";
        }
    }
}
StudentClassDashboard.template = "student_class.StudentClassDashboard";
