/** @odoo-module **/
import {
    StatusBarButtons
} from '@web/views/form/status_bar_buttons/status_bar_buttons';
import {
    patch
} from '@web/core/utils/patch';
const {
    useRef,
    useState,
    onMounted
} = owl;
import {
    useBus
} from "@web/core/utils/hooks";

patch(StatusBarButtons.prototype, {
    setup() {
        super.setup();
        this.state = useState({
            isVisible: true,
            hasSheet: true
        });
        this.buttonRef = useRef('cy-Button');
//        this.env.bus.addEventListener('buttonRemove', this.onCancelClick.bind(this));
        onMounted(() => this.onMounted());
        useBus(this.env.bus, 'REMOVE_BUTTON_PROPERTIES', ({ detail }) => {
            this.state.hasSheet = true
            this.state.isVisible = true
        });
    },

    onMounted() {
        const sheet = document.querySelector('.o_form_sheet')?.getAttribute('sheet')
        console.log("Sheets", sheet)
        console.log("Sheets22", this.buttonRef.el)
        if (sheet) {
            this.state.hasSheet = false
        }
        const self = this
        const button = this.buttonRef.el
        console.log("Sheets22", button)
        var drake = dragula([this.buttonRef.el], {
                revertOnSpill: true,
                moves: (el, container, handle) => {
                    return !el.classList.contains('cy-add-button');
                },
                accepts: (el, target, source, sibling) => {
                    return sibling
                }
            })
            .on('drop', async function(el, target, source, sibling) {
                const buttonPath = el.getAttribute('cy-xpath');
                const siblingPath = sibling.getAttribute('cy-xpath')
                const path = siblingPath || '/form/header';
                const position = siblingPath ? 'before' : 'inside';
                console.log("BttnPath", buttonPath)
                console.log("BttnPath", siblingPath)
                console.log("BttnPath", path)
                console.log("BttnPath", position)
                self.env.services.ui.block();
                try {
                    const response = await self.env.model.rpc("cyllo_studio/move/button", {
                        method: 'move_button',
                        kwargs: {
                            path,
                            position,
                            buttonPath,
                            model: self.env.model.action.currentController.action.res_model,
                            view_id: self.env.config.viewId,
                            view_type: self.env.config.viewType,
                        }
                    })
                    if (response) {
                        let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                        let cleanedStr = response.replace(/\s+/g, ' ').trim();
                        storedArray.push(cleanedStr)
                        sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                        sessionStorage.setItem('ReDO', JSON.stringify([]));
                    }
                } finally {
                    self.env.services.ui.unblock();
                }
                self.env.model.action.doAction('studio_reload')
            });
    },

    async addNewButton() {
        //        const header =  this.buttonRef.el.closest('.o_form_statusbar');
        console.log("AddNdwBttns", this, this.buttonRef.el.closest('.o_form_statusbar').getAttribute('studio-header'))
        const header = this.buttonRef.el.closest('.o_form_statusbar');
        console.log("AddNdwBttn11", header)
        const newHeader = header.getAttribute('studio-header');
        console.log("NewwBttn", newHeader)
        const cyXpath = header.getAttribute('cy-xpath');
        console.log("AddNdwBttn22", cyXpath)
        if (!header) return;
        this.state.isVisible = false;
        this.env.bus.trigger('BUTTON_DETAILS', {
            type: "ButtonProperties",
            path: cyXpath || "",
            position: "inside",
            newButton: true,
            newHeader,
        });
    },

//    async onCancelClick() {
//        const button = document.querySelector('.btn.btn-secondary[name="action_new_button"]');
//        if (button) button.remove();
//        this.env.bus.trigger('CancelButtonClicked');
//    },
});
StatusBarButtons.template = 'cyllo_studio.Button'