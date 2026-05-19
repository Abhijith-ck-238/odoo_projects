/** @odoo-module  */
import {
    ButtonBox
} from "@web/views/form/button_box/button_box";
import {
    patch
} from '@web/core/utils/patch';
import {
    useService
} from "@web/core/utils/hooks";
import {
    onWillUnmount
} from "@odoo/owl";
import {
    _t
} from "@web/core/l10n/translation";

const {
    useRef,
    useState,
    onWillRender,
    onMounted
} = owl;

patch(ButtonBox.prototype, {
    setup() {
        //        super.setup();
        console.log("BttnBx", this)
        this.action = useService("action");
        this.rpc = useService("rpc");
        this.ref = useRef('cy-ButtonBox')
        this.state = useState({
            //            addSmartButtonIcon: true,
            //            clicked: false,
            //            isX2Many: sessionStorage.getItem('CyX2ManyPath')
        });
        //        this.effect = useService("effect");
        onWillRender(() => {
            //            this.state.isX2Many = sessionStorage.getItem('CyX2ManyPath')
            this.visibleButtons = Object.entries(this.props.slots)
                .filter(([_, slot]) => this.isSlotVisible(slot))
                .map(([slotName]) => slotName)
            this.additionalButtons = [];
            this.isFull = true;
        });
        onMounted(this.onMounted)
        //        this.handleAutoSave = async (ev) => await this.AutoSave(ev);
        //        onMounted(() => {
        //            this.handleListener()
        //            const sheet = document?.querySelector('.o_form_sheet')?.getAttribute('sheet')
        //            if (sheet) {
        //                this.state.addSmartButtonIcon = false
        //            }
        //        });
        //        onWillUnmount(() => this.handleListener(false))
    },
    //    handleListener(isAdd = true) {
    //        if (isAdd) {
    //            document.addEventListener("click", this.handleAutoSave, {capture: true});
    //            document.addEventListener("mousedown", this.handleAutoSave, {capture: true});
    //        } else {
    //            document.removeEventListener("click", this.handleAutoSave, {capture: true});
    //            document.removeEventListener("mousedown", this.handleAutoSave, {capture: true});
    //        }
    //    },
    //    AutoSave(ev) {
    //        const dialog = document.querySelector(".o_technical_modal") || document.querySelector(".o_error_dialog");
    //        const view = document.querySelector(".o_form_view")
    //        if (this.state.clicked && view.contains(ev.target) && !dialog) {
    //            ev.stopPropagation();
    //            return this.effect.add({
    //                title: _t("Validation Error"),
    //                message: "Unable to save the smart button.",
    //                description: "Please click save or cancel before making another changes",
    //                type: "notification_panel",
    //                notificationType: "warning",
    //            });
    //        }
    //    },
    //
    onMounted() {
        console.log("OnMountedd", this)
        const self = this
        const smart_button = this.ref.el
        console.log("SmartBttn", smart_button)
        const drake = dragula([smart_button], {
                revertOnSpill: true,
                moves: (el, container, handle) => {
                    return !el.classList.contains('cy-add-smart-button');
                },
                accepts: (el, target, source, sibling) => {
                    return sibling
                }
            })
            .on('drop', function(el, target, source, sibling) {
                console.log("Drp", el)
                console.log("Drp", target)
                console.log("Drp", source)
                console.log("Drp", sibling)
                const {
                    config,
                    services,
                    bus
                } = self.env;
                const model = self.action.currentController.action.res_model;
                const viewId = config.viewId || null;

                // Cache attributes
                const smartButtonPath = el?.getAttribute('cy-xpath');
                const siblingPath = sibling?.getAttribute('cy-xpath');
                const sourcePath = source?.getAttribute('cy-xpath');

//                const path = siblingPath || sourcePath;
                if (!(siblingPath || sourcePath) || !smartButtonPath || !model) {
                    console.warn("Required data missing for smart button move");
                    return;
                }

                const position = siblingPath ? 'before' : 'inside';

                services.ui.block();

                self.rpc("cyllo_studio/move/smart_button", {
                    kwargs: {
                        sourcePath: siblingPath || sourcePath,
                        position,
                        smartButtonPath,
                        model,
                        view_id: viewId,
                        viewType: 'form',
                    }
                }).then((response) => {
                    if (response?.trim()) {
                        // Minimize parsing/writing
                        const undoList = sessionStorage.getItem('UndoRedo');
                        const storedArray = undoList ? JSON.parse(undoList) : [];

                        storedArray.push(response.replace(/\s+/g, ' ').trim());

                        sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                        sessionStorage.setItem('ReDO', '[]');
                    }

                    services.ui.unblock();
                    self.action.doAction('studio_reload');
                    bus.trigger('resetProperties');
                }).catch((err) => {
                    services.ui.unblock();
                    console.error("RPC failed:", err);
                });
            });
    },
    //
    async addSmartButton(e) {
        console.log("AddsMartBBtn", e, this)
        const buttonBoxExists = document.querySelector('.button-box-container') !== null;
        const pathElement = document.querySelector('.o-form-buttonbox');
        console.log("asdasdasdasdas", document.querySelector('.o-form-buttonbox'))

        const path = pathElement?.getAttribute('cy-xpath');
        const parent = e.target.closest(".oe_stat_button");

        if (parent) {
            parent.insertAdjacentHTML('beforebegin', `
                <button class="btn dummy-smart-button oe_stat_button btn-outline-secondary flex-grow-1 flex-lg-grow-0">
                    <i class="o_button_icon fa fa-fw fa-file-text-o me-1"></i>
                    <div class="o_field_widget o_readonly_modifier o_field_statinfo">
                        <span class="o_stat_info o_stat_value">0</span>
                        <span class="o_stat_text">Smart Button</span>
                    </div>
                </button>
            `);
        }

        this.env.bus.trigger('SMART_BUTTON_DETAILS', {
            properties: {
                new_button: true
            },
            addButtonBox: buttonBoxExists,
            path,
            type: "SmartButtonProperties",
            new_button: true
        });
    },
});

ButtonBox.props = {
    ...ButtonBox.props,
    cyXpath: {
        type: String,
        optional: true
    },
    striped: {
        type: Boolean,
        optional: true
    }, // Add the `striped` prop
}
ButtonBox.template = 'cyllo_studio.ButtonBox'