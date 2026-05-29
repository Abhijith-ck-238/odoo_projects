/** @odoo-module **/
const { Component, useState, onMounted, useExternalListener } = owl;
import { ExpressionEditorDialog } from "@web/core/expression_editor_dialog/expression_editor_dialog";
import { useOwnedDialogs, useService } from "@web/core/utils/hooks";
import { handleUndoRedo } from "@cyllo_studio/js/utils/undo_redo_utils";
import { _t } from "@web/core/l10n/translation";

export class RibbonProperties extends Component {
    static template = 'cyllo_studio.RibbonProperties';

    setup() {
        console.log("this", this);
        this.addDialog = useOwnedDialogs();
        this.notification = useService('notification');
        this.action = useService('action');
        this.rpc = useService('rpc');

        this.state = useState({
            showDropdown: false
        });

        this.properties = useState({
            string: '',
            color: 'text-bg-danger',
            invisible: 'False',
        });

        this.saveHandled = false;
        this.AutoSave = async (ev) => await this.handleAutoSave(ev);
        onMounted(() => {
            this.action_area= document.querySelector(".o_action_manager")
                console.log("escapeddddddddd",document.querySelector(".o_action_manager"))
                console.log("escapeddddddddd",document)
        });
        useExternalListener(document, 'click', this.AutoSave, { capture: true });
        useExternalListener(document, 'mousedown', this.AutoSave, { capture: true });
    }
async handleAutoSave(ev) {
    if (!this.action_area.contains(ev.target)) return;
    if (ev.type === 'mousedown') {
        this.saveHandled = true;
    } else if (ev.type === 'click' && this.saveHandled) {
        this.saveHandled = false;
        return;
    }
        this.env.services.ui.block();
    try {
        console.log("rpc callllllllll");
        const response = await this.rpc("cyllo_studio/kanban/add/ribbon", {
            path: this.props.properties.elementInfo.path,
            position: this.props.properties.elementInfo.position,
            ...this.props.viewDetails,
            properties: { ...this.properties },
        });
        if (response) {
            handleUndoRedo(response);
        }
    } finally {
        this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
}

    get colors() {
        return {
            'text-bg-primary': 'Primary',
            'text-bg-secondary': 'Secondary',
            'text-bg-success': 'Success',
            'text-bg-info': 'Info',
            'text-bg-warning': 'Warning',
            'text-bg-danger': 'Danger'
        };
    }

    handleSelectColor(color) {
        console.log("Selected color:", color);
        this.properties.color = color;
        this.state.showDropdown = false;
        this.props.element.firstChild.className = color;
    }

    handleLabelChange({ target }) {
        console.log("Label changed:", target.value);
        this.props.element.firstChild.textContent = target.value;
        this.properties.string = target.value;
    }
}

