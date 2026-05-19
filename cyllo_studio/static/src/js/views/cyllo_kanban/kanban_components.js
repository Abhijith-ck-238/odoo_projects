/** @odoo-module **/
import {
	Component,
	useState,
	useRef,
	useEffect,
	onMounted,
} from "@odoo/owl";
import {
	useService
} from "@web/core/utils/hooks";
import { KanbanFieldDialog } from "./kanban _field_dialog"
import { scaleMapping } from "./cyllo_kanban_record"
export class KanbanComponents extends Component {
	static template = "cyllo_studio.KanbanComponents";
	setup() {
 		this.rpc = useService("rpc");
		this.action = useService("action");
		this.dialog = useService("dialog");
		this.componentRef = useRef("ComponentRef")
		this.state = useState({
		    toggle: false,
		    top: 0,
		    left: 0,
		})
		onMounted(()=> {
		    const self = this
		    const draggableComponent = this.componentRef.el
		    const kanbanRecord = document.getElementById("cyKanbanRecord")

		    const scaleKey = sessionStorage.getItem('kanbanScale') || '100%'
		    const scale = scaleMapping[scaleKey] || 1
		    this.state.top = kanbanRecord.offsetTop
		    this.state.left = kanbanRecord.offsetLeft + scale * kanbanRecord.offsetWidth + 10;
//		                if(draggableComponent){
//             }



		})
		useEffect(()=>{
		    if(this.state.toggle){
		        return;
		    }
            const self = this
		    const draggableComponent = this.componentRef.el
		    console.log("draggableComponent",draggableComponent)
		    const component = draggableComponent.querySelector('.cy-studio-kanban-component');
		    console.log("component",component)
		    const kanbanRecord = document.getElementById("cyKanbanRecord")
		    console.log("kanbanRecord",kanbanRecord)

            const divElements = Array.from(kanbanRecord?.querySelectorAll('[data-drag="1"]') || []);

		    const button = `<button class="cy-listBtn btn btn-secondary oe_kanban_action oe_kanban_action_button text-wrap"><span>Button</span></button>`
            const field = `<span>Field</span>`

            if (component && divElements.length) {
                let ribbonPath = divElements[0].getAttribute('cy-xpath');
                let ribbonPosition = 'inside';

                if (divElements[0].firstElementChild) {
                    ribbonPath = divElements[0].firstElementChild.getAttribute('cy-xpath');
                    ribbonPosition = 'before';
                }

                const drake = dragula([component, ...divElements], {
                    revertOnSpill: true,
                    copy: true,
                    moves: (el, source) => component === source,
                    accepts: (el, target, source) => {
                        if (el.classList.contains('cy-studio-ribbon')) {
                            return divElements[0] === target;
                        } else {
                            return divElements.includes(target);
                        }
                    },
                });
                drake.on('drag', (el) => {
                    divElements.forEach((element) => {
                        element.classList.add('cy-studio-kanban-container');
                    });
                }).on('dragend', () => {
                    divElements.forEach((element) => {
                        element.classList.remove('cy-studio-kanban-container');
                    });
                }).on('cloned', (clone) => {
                    clone.classList.remove('cy-studio-icon', 'bg-secondary', 'rounded', 'px-2', 'py-1', 'border', 'border-white', 'text-white', 'cy-component-container', 'kanban-component-text');
                    clone.removeAttribute('data-tooltip');

                    if (clone.classList.contains('cy-studio-field') || clone.classList.contains('cy-studio-button') || clone.classList.contains('cy-studio-text') || clone.classList.contains('cy-studio-div')) {
                        clone.classList.add('border-class', 'd-flex', 'justify-content-around', 'align-items-center');
                    } else if (clone.classList.contains('cy-studio-ribbon')) {
                        clone.classList.add('ribbon', 'ribbon-top-right');
                        clone.style.zIndex = '10';
                        clone.style.opacity = '1';
                        clone.innerHTML = `<span class="text-bg-danger"></span>`;
                    }
                }).on('drop', async (el, target, source, sibling) => {
                    const siblingPath = sibling?.getAttribute('cy-xpath');
                    const targetPath = target.getAttribute('cy-xpath');
                    const path = siblingPath || targetPath;
                    const position = siblingPath ? 'before' : 'inside';
                    const matchingClass = Array.from(el.classList).find(cls => cls.startsWith('cy-studio-'));

                    const x2many = this.props.x2many;
                    this.env.bus.trigger('resetProperties');
                    const properties = {
                        elementInfo: {
                            path,
                            position,
                        },
                        viewDetails: {
                            model: self.action.currentController.props.resModel,
                            view_type: self.env.config.viewType,
                            view_id: self.env.config.viewId,
                        },
                    };

                    let item;
                    switch (matchingClass) {
                        case 'cy-studio-button':
                            item = 'button';
                            break;
                        case 'cy-studio-field':
                            item = 'field';
                            break;
                        case 'cy-studio-text':
                            item = 'text';
                            break;
                        case 'cy-studio-div':
                            item = 'div';
                            break;
                        case 'cy-studio-ribbon':
                            item = 'ribbon';
                            properties.elementInfo.path = ribbonPath;
                            properties.elementInfo.position = ribbonPosition;
                            break;
                    }
                    if (item === 'field') {
                         self.dialog.add(KanbanFieldDialog, {
                            ...properties,
                            fields: this.props.fields,
                            x2many: x2many,
                        });
                    }
                     else if(item= ='ribbon') {
                         self.env.bus.trigger('KANBAN_COMPONENT', {
                            type: item,
                            properties,
                            element:el,

                        });
                    }
                    else if(item == 'button') {
                        self.env.bus.trigger('KANBAN_COMPONENT', {
                            type: item,
                            properties,
                        });
                        }
                        else if(item == 'text') {

                        self.env.bus.trigger('KANBAN_COMPONENT', {
                            type: item,
                            properties,
                            element:el,
                        });
                        }

                    if (item === 'div') {
                        console.log(12313131231231)
                        self.env.services.ui.block();
                       console.log("properties.elementInfo",properties)
                        try {
                            const response = await self.rpc("cyllo_studio/kanban/add/div", {
                                ...properties.elementInfo,
                                ...properties.viewDetails,
                            });

                        } finally {
                            self.env.services.ui.unblock();
                        }
                     }
                });
    }

		},
		()=> [this.state.toggle])



	}


}