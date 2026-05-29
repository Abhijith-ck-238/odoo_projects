/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { _t } from "@web/core/l10n/translation";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { StatusBarField } from "@web/views/fields/statusbar/statusbar_field";
import { useService } from "@web/core/utils/hooks";

// Updated the onclick functionality of statusbar
patch(StatusBarField.prototype,{
    setup(){
        super.setup()
        this.dialog = useService("dialog");
    },
    async selectItem(item) {
    // **Show the confirmation dialog before Changing status**
        this.dialog.add(ConfirmationDialog, {
            title: _t("Move Task"),
            body: _t("Are you sure you want change the status of this record ?"),
            confirm: () => {
            // Change the record only if confirmed is selected
                super.selectItem(item);
            },
            cancel: () => {},
        });
    }
})

patch(KanbanRenderer.prototype, {
    async sortRecordDrop(dataRecordId, dataGroupId, { element, parent, previous }) {
        element.classList.remove("o_record_draggable");

        if (
            !this.props.list.isGrouped ||
                  parent.classList.contains("o_kanban_hover") ||
            parent.dataset.id === element.parentElement.dataset.id
        ) {
            if (parent && parent.classList) {
                parent.classList.remove("o_kanban_hover");
            }
            while (previous && !previous.dataset.id) {
                previous = previous.previousElementSibling;
            }

            const refId = previous ? previous.dataset.id : null;
            const targetGroupId = parent && parent.dataset.id;

            // **Show the confirmation dialog before moving the record**
            this.dialog.add(ConfirmationDialog, {
                title: _t("Move Task"),
                body: _t("Are you sure you want change the status of this record ?"),
                confirm: () => {
                        // Move the record only if confirmed
                        this.props.list.moveRecord(dataRecordId, dataGroupId, refId, targetGroupId);
                },
                cancel: () => {},
            });
        }
        element.classList.add("o_record_draggable");
    },
});

