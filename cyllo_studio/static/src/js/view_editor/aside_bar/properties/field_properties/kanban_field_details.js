/** @odoo-module **/

import {
	Component,
	useState,
	onMounted
} from "@odoo/owl";
import {
	useService,
	useOwnedDialogs
} from "@web/core/utils/hooks";
import {
	ExpressionEditorDialog
} from "@web/core/expression_editor_dialog/expression_editor_dialog";
export class KanbanFieldProperties extends Component {
	static template = "cyllo_studio.KanbanFieldProperties";

	setup() {
		console.log("kanbaniiiinnnnn this", this)
		this.rpc = useService("rpc");

		this.actionService = useService("action");
		this.action = useService("action");
		this.orm = useService("orm");
		this.addDialog = useOwnedDialogs();

		this.state = useState({
			widget: this.props.widget,
			path: this.props.path,
			fieldInvisible: this.props.invisible || false,
			widget_value: this.props.widget ? this.props.widget : false,
			defaultWidgets: []

		});

	}

	undoOperation(response){
        let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
        let cleanedStr = response.replace(/\s+/g, ' ').trim();
        storedArray.push(cleanedStr);
        sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
        sessionStorage.setItem('ReDO', JSON.stringify([]));
    }

	handleInvisibleChange(event) {
		this.state.fieldInvisible = event.target.checked ? 'True' : 'False'
	}
	async attrDomain(ev) {
	    console.log("ythj", this)
		const parent = ev.target.closest('.cy-basedOn');
		var attribute = parent.getAttribute('data-attribute');
		console.log("parent", parent)
		console.log("attribute", attribute)
		var domain = '';
		if (attribute === 'invisible' && (this.state.item_name?.props.fieldInfo.invisible || this.state.fieldInvisible)) {
			domain = this.state.fieldInvisible ? this.state.fieldInvisible : this.state.item_name.props.fieldInfo.invisible;
		} else {
			domain = false;
		}
		console.log("domain", domain)
		var resModel = this.action.currentController.props.resModel;
		domain = domain ? domain : "False";

		this.addDialog(ExpressionEditorDialog, {
			resModel,
			fields: this.props.allFields,
			expression: domain,
			onConfirm: (expression) => this.modifier(expression, attribute),
		});
	}
	modifier(expression, attribute) {
		this.attribute = attribute
		if (attribute === 'invisible') {
			this.state.fieldInvisible = expression
		}
	}

	async updateKanban(){
	    console.log("hsdoidsfs props :", this.props)
	    console.log("hsdoidsfs model :", this.props.model)
	    console.log("hsdoidsfs viewID:", this.props.viewId)
	    console.log("hsdoidsfs viewType :", this.props.viewType)
	    console.log("hsdoidsfsss path :", this.props.path)
	    console.log("hsdoidsfs widget_value :", this.state.widget_value)
	    console.log("hsdoidsfs fieldInvisible :", this.state.fieldInvisible)
	    console.log("hsdoidsfs activeFields :", this.props.activeFields)
	    const args = {
	        model: this.props.model,
            view_id: this.props.viewId,
            view_type: this.props.viewType,
            path: this.props.path,
            widget: this.state.widget_value,
            invisible:this.state.fieldInvisible,
            active_fields:this.props.activeFields
	    }
         const response = await this.rpc("cyllo_studio/kanban/update/field", { args });
//        if(response){
//            this.undoOperation(response)
//        }
	}


	async RemoveField(){
	    console.log("RmvFieldss", this)
//        const path = this.props.path
//        const regex = /field(\[\d+\])?$/;
//        let isChildField = false;
//        const childNames = [];
//        const element = this.props.element
//        for (let i = 0; i < element?.children.length; i++) {
//            const childPath = element.children[i].getAttribute('cy-xpath');
//            const childName = element.children[i].getAttribute('name');
//            if (regex.test(childPath)) {
//                isChildField = true;
//            }
//            if (childName) {
//                childNames.push(childName);
//            }
//        }
//        const fieldName = this.props.name
//        const isField = regex.test(path);
//        let field = ""
//        if(isField){
//            const fieldNodes = this.props.fieldNodes;
//            const nameExists = Object.keys(fieldNodes).filter(element => element.startsWith(fieldName));
//            let isPathIncluded = nameExists.some(name => fieldNodes[name].MainPath.includes('/kanban/field'));
//            field = isPathIncluded ? "" : fieldName
//        }
//        let childField = ""
//        if(isChildField){
//            const fieldNodes = this.props.fieldNodes;
//            const nameExists = Object.keys(fieldNodes).filter(element => element.startsWith(childNames));
//            let isPathIncluded = nameExists.some(name => fieldNodes[name].MainPath.includes('/kanban/field'));
//            childField = isPathIncluded ? "" : childNames
//        }
//        const response =  await this.rpc("cyllo_studio/delete/kanban/field", {
//            model: this.props.model,
//            view_id: this.props.viewId,
//            view_type: this.props.viewType,
//            path: this.props.path,
//            field_name: field,
//            child_field_name: childField,
//        });
//        if(response){
//            this.undoOperation(response)
//        }
//        this.env.bus.trigger("CLEAR-MENU");
//        this.action.doAction('studio_reload');
    }

}