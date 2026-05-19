/** @odoo-module **/
import {
	Component,
	onWillStart,
	useEffect,
	onWillUpdateProps,
	useState
} from "@odoo/owl";
import {
	CylloStudioDropdown
} from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import {
	_t
} from "@web/core/l10n/translation";
import {
	sortBy
} from "@web/core/utils/arrays";
import {
	validateField
} from "@cyllo_studio/js/actions/utils";

export class ListOverall extends Component {
	static template = "cyllo_studio.ListOverall";
	setup() {
        this.state = useState({
            invisible : false
        })
		onWillStart(() => {
            this.state.invisible =  sessionStorage.getItem('invisible');
			const {
				activeFields = {}, allFields = {}
			} = this.props;
			if (Object.keys(activeFields).length && Object.keys(allFields).length) {
				this.currentField = Object.keys(activeFields).reduce(
					(acc, fieldName) => {
						acc[fieldName] = allFields[fieldName];
						return acc;
					}, {}
				);
				console.log("fields", this.currentField)
				const fields = Object.entries(this.currentField)
					.filter(([fieldName, field]) => validateField(fieldName, field))
					.map(([fieldName, field]) => ({
						name: fieldName,
						...field
					}));
				this.fields = sortBy(fields, "string");
				console.log("fields2", this.fields)
			}
		});
		onWillUpdateProps(async (nextProps) => {
			const {
				activeFields = {}, allFields = {}
			} = this.props;
			if (Object.keys(activeFields).length && Object.keys(allFields).length) {
				this.currentField = Object.keys(activeFields).reduce(
					(acc, fieldName) => {
						acc[fieldName] = allFields[fieldName];
						return acc;
					}, {}
				);
				console.log("fields", this.currentField)
				const fields = Object.entries(this.currentField)
					.filter(([fieldName, field]) => validateField(fieldName, field))
					.map(([fieldName, field]) => ({
						name: fieldName,
						...field
					}));
				this.fields = sortBy(fields, "string");
				console.log("fields2", this.fields)
			}

		});

	}

	get position() {
		const value = ["top", "bottom", ""];
		const position = [
			" Add Record At Top",
			" Add Record At Bottom",
			" Open Form View",
		];
		const arr = [];
		for (let i = 0; i < value.length; i++) {
			const obj = {
				value: value[i],
				label: position[i],
			};
			arr.push(obj);
		}
		return arr;
	}
	get defaultSortValue() {
		return this.props.mode.defaultOrder?.[0]?.name || null;
	}
	get defaultPosition() {
		return this.props.mode.editable || "";
	}
	generateRandomFieldName() {
		const timestamp = Date.now();
		const randomChars = Math.random().toString(36).substring(2, 7); // Random alphanumeric string of length 5
		const randomNum = Math.floor(Math.random() * 1000);
		return `x_studio_${timestamp}_${randomNum}_${randomChars}`;
	}
	async handleView(name, value = null, state = null, field = null, order = null) {
		console.log("asdasdasdas")
	}

	get sortValues() {
		console.log("qwertyu", this)
		console.log("qwertyu", this.fields)
		console.log("qwertyu", this.this.fields)
		const arr = [];
		for (let value in this.fields) {
			const obj = {
				value: this.fields[value].name,
				label: this.fields[value].string,
			};
			arr.push(obj);
		}
		return [{
			value: "",
			label: ""
		}, ...arr];
	}
}
ListOverall.components = {
	CylloStudioDropdown,
};