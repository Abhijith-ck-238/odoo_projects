/** @odoo-module **/
import {
    Component,
    onMounted,
    useState,
    useEffect,
    useRef,
    onWillStart,
    onWillUpdateProps,
    useExternalListener,
} from "@odoo/owl";
import {
    useService,
    useOwnedDialogs
} from "@web/core/utils/hooks";
import {
    CylloStudioDropdown
} from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";
import {
    registry
} from "@web/core/registry";
import {
    handleUndoRedo
} from "@cyllo_studio/js/utils/undo_redo_utils";
import {
    ExpressionEditorDialog
} from "@web/core/expression_editor_dialog/expression_editor_dialog";
import {
    _t
} from "@web/core/l10n/translation";
import {
    getWidgetTypes,
    getWidgetSupport
} from "@cyllo_studio/js/view_editor/widget"
import {
    DomainSelectorDialog
} from "@web/core/domain_selector_dialog/domain_selector_dialog";


export class FieldProperties extends Component {
    static template = "cyllo_studio.FieldProperties";
    static props = {
        attr: {
            type: Object,
            optional: true
        },
        allFields: {
            type: Object,
            optional: true
        },
        type: {
            type: String,
            optional: true
        },
        name: {
            type: String,
            optional: true
        },
        string: {
            type: String,
            optional: true
        },
        label: {
            type: String,
            optional: true
        },
        widget: {
            type: String,
            optional: true
        },
        fieldType: {
            type: String,
            optional: true
        },
        context: {
            type: String,
            optional: true
        },
        viewType: {
            type: String,
            optional: true
        },
        model: {
            type: String,
            optional: true
        },
        viewId: {
            type: Number,
            optional: true
        },
        type: {
            type: String,
            optional: true
        },
        create: {
            type: Boolean,
            optional: true
        },
        placeholder: {
            type: String,
            optional: true

        },
        help: {
            type: String,
            optional: true

        },
        edit: {
            type: Boolean,
            optional: true
        },
        readonly: {
            type: String,
            optional: true

        },
        invisible: {
            type: String,
            optional: true

        },
        required: {
            type: String,
            optional: true

        },
        related_model: {
            type: String,
            optional: true

        },
        domain: {
            type: String,
            optional: true
        },
        field_path: {
            type: String,
            optional: true

        },
        path: {
            type: String,
            optional: true

        },
        widget_types: {
            type: Object,
            optional: true

        },
        options: {
            type: Object,
            optional: true

        },

    };
    setup() {
        this.actionService = useService("action");
        this.action = useService("action");
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
        this.rpc = useService("rpc");
        this.notification = useService("effect");
        this.addDialog = useOwnedDialogs();
        this.ref = useRef('cy-Properties')
        this.prevState = useState({
            ...this.props
        })
        this.state = useState({
            xStudio: 0,
            name: this.props.name,
            string: this.props.string,
            related_model: this.props.related_model,
            widget: this.props.widget,
            help: this.props.help,
            placeholder: this.props.placeholder,
            invisible: this.props.invisible,
            readonly: this.props.readonly,
            required: this.props.required,
            relatedModel: "",
            relatedModelField: "",
            field_path: this.props.field_path,
            edited: false,
            fieldType: [
                "Char",
                "Text",
                "Html",
                "Integer",
                "Float",
                "Date",
                "Datetime",
                "Binary",
                "Selection",
                "Boolean",
                "Many2one",
                "One2many",
                "Many2many",
            ],
            models: [],
            domain: this.props.domain || '',
            inverseFields: [],
            selectedFieldType: this.props.fieldType || 'char',
            widget_types: [],
            context: '{}',
            //            selectedFieldType :  'char',
        });
        this.selectedWidget = this.props.widget === 'False' ? '' : this.props.widget || ''
        onWillUpdateProps((nextProps) => {
            this.state.name = nextProps.name
            this.state.string = nextProps.string
            this.state.related_model = nextProps.related_model
            this.state.widget = nextProps.widget
            this.state.selectedFieldType = nextProps.fieldType
            this.state.help = nextProps.help
            this.state.placeholder = nextProps.placeholder
            this.state.invisible = nextProps.invisible
            this.state.readonly = nextProps.readonly
            this.state.required = nextProps.required
        });
        useEffect(() => {
            if (this.props.edit != true) {
                return
            } else {
                const CurrWidget = this.props.widget
                this.widgetOptionalFields(CurrWidget, this.props.options)
            }
        }, () => [this.props.edit])

        onMounted(async () => {
            this.state.widget_types = getWidgetTypes(this.props.fieldType)
            this.action_area = document.querySelector(".o_action_manager")
            const fieldsData = await this.orm.searchRead(
                "ir.model.fields",
                [
                    ["model_id", "=", this.props.model]
                ],
                ["name"]
            );
            const studioFields = fieldsData.filter((field) =>
                field.name.startsWith("x_studio")
            );
            this.state.xStudio = studioFields.length;
            this.state.models = await this.rpc('/cyllo_studio/get_non_abstract_non_transient_models');
        });



    }

    generateRandomFieldName() {
        const timestamp = Date.now();
        const randomNum = Math.floor(Math.random() * 1000);
        return `x_studio_${timestamp}_${randomNum}`;
    }

    onCellKeydown(value) {
        this.state.edited = true
        const labelValue = this.ref.el.querySelector("#label").value.trim();
        this.state.name = 'x_studio_' + labelValue.toLowerCase().split(' ').join('_');
    }
    get fieldType() {
        const result = this.state.fieldType.map((item) => ({
            value: item,
            label: item
        }));
        return result;
    }
    RelatedModel(array) {
        const result = array.map((item) => ({
            value: item.model,
            label: item.name,
        }));
        return result;
    }
    handleFieldTypeChange(value) {
        this.state.edited = true
        this.selectedWidget = ''
        const container = document.getElementById('dynamic-container');
        while (container && container.firstChild) {
            container.removeChild(container.firstChild);
        }
        this.state.selectedFieldType = value.toLowerCase()
        this.state.widget_types = getWidgetTypes(this.state.selectedFieldType)
        console.log("hjv", this)
    }
    fieldsDomain() {
        //        const FieldDomain = this.state.item_name?.props?.fieldInfo
        const ModelName = this.props.model
        this.dialogService.add(DomainSelectorDialog, {
            resModel: ModelName,
            domain: this.state.domain,
            onConfirm: (domain) => this.domainConfirm(domain),
            title: ("Domain"),
        });
    }
    domainConfirm(domain) {
        this.state.domain = domain
    }
    deleteField() {
        if (this.props.create) {
            this.action.doAction('studio_reload')
            this.env.bus.trigger('CLEAR-MENU');
        }

    }
    async createField() {
        let args = {}
        var optionalFields = {};
        var container = document.getElementById('dynamic-container');
        if (container) {
            console.log("dfdf01", optionalFields)
            container.querySelectorAll('input, select').forEach(field => {
                const fieldName = field.id;
                let fieldValue;
                if (fieldName === "create") {
                    fieldValue = [];
                    const inputValue = field.type === "checkbox" ? field.checked : field.value;
                    if (inputValue !== undefined && inputValue !== null && inputValue !== "") {
                        fieldValue.push(inputValue);
                    }
                } else {
                    console.log("dfdf02", optionalFields)
                    if (field.name == "fold_field") {
                        this.orm.searchRead("ir.model.fields", [
                                ['model', '=', this.state.relatedModel]
                            ])
                            .then((fields) => {
                                const foldFieldExists = fields.some(f => f.name === 'fold');
                                if (foldFieldExists) {
                                    fieldValue = field.checked ? "fold" : "";
                                } else {
                                    this.action.doAction({
                                        type: 'ir.actions.client',
                                        tag: 'display_notification',
                                        params: {
                                            message: 'Related model must condine fold field',
                                            type: 'danger',
                                            sticky: false,
                                        },
                                    });
                                }
                            });
                    } else {
                        fieldValue =
                            field.type === "checkbox" ? field.checked : field.value;
                    }
                }
                if (fieldValue !== 'undefined' && fieldValue !== null && fieldValue !== "") {
                    optionalFields[fieldName] = fieldValue;
                }
                if (typeof fieldValue === 'string' && fieldValue.startsWith('[') && fieldValue.endsWith(']')) {
                    fieldValue = fieldValue.replace(/'/g, '"');
                    fieldValue = JSON.parse(fieldValue);
                    optionalFields[fieldName] = fieldValue;
                }
            });
            const customSelector = container.querySelectorAll('.cy-studio-custom-dropdown-image-widget')
            const startDateField = customSelector[0]?.id;
            const endDateField = customSelector[1]?.id;
            console.log("dfdf", this)
            console.log("dfdf", optionalFields)
            console.log("dfdf", customSelector)
            if (optionalFields[customSelector[0]?.attributes.id.value]) {
                console.log("sdff", optionalFields)
                console.log("sdff", customSelector[0])
                console.log("sdff", customSelector[0]?.attributes)
                console.log("sdff", customSelector[0]?.attributes.id.value)
                optionalFields[customSelector[0]?.attributes.id.value] = this.state.previewImage[startDateField] || ""
            }
            if (customSelector[1]?.attributes) {
                optionalFields[customSelector[1]?.attributes.id.value] = this.state.previewImage[endDateField] || ""
            }
        }
        console.log("jjff", optionalFields)
        if (this.props.edit) {
            const value = this.getCurrentChanges(this.prevState, this.state)
            args = {
                value,
                edit: this.props.edit,
                field_path: this.props.field_path || this.props.path,
            }
        } else {
            const attrs = {
                widget: this.state.widget || '',
                help: this.state.help || '',
                placeholder: this.state.placeholder || '',
                invisible: this.state.invisible || '',
                readonly: this.state.readonly || '',
                required: this.state.required || '',
                domain: this.state.domain || '',
                context: this.state.context || '',
            }
            args = {
                edit: this.props.edit,
                field_type: this.state.selectedFieldType || 'char',
                optional_fields: optionalFields,
                technical_name: this.state.name,
                label: this.state.label || '',
                cy_path: this.props.path || '',
                field_path: this.props.path,
//                elementType: "",
                related_model: this.state.related_model || null,
                attrs

                //                related_model_field: related_model_field,
            };
        }
        try {
            if (args) {
                const response = await this.rpc("cyllo_studio/list/create/new_fields", {
                    method: 'create_new_fields',
                    model: this.props.model,
                    view_id: this.props.viewId,
                    view_type: this.props.viewType,
                    args: [args],
                })
                if (response) {
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
            }
        } finally {
            this.env.services.ui.unblock();
            //             this.action.doAction('studio_reload')
            this.env.bus.trigger("ASIDE-MENU");
            //              window.location.reload();
        }

    }
    getCurrentChanges(prev, current) {
        const changed = {};
        const excludedKeys = ['fieldType', 'widget_types'];
        for (const key in current) {
            if (prev[key] !== undefined && !excludedKeys.includes(key) && prev[key] !== current[key]) {
                changed[key] = current[key];
            }
        }
        return changed;
    }
    handleInvisibleChange(event) {
        this.state.edited = true
        this.state.invisible = event.target.checked ? 'True' : 'False'
    }
    handleReadonlyChange(event) {
        this.state.edited = true
        this.state.readonly = event.target.checked ? 'True' : 'False'
    }
    handleRequiredChange(event) {
        this.state.required = event.target.checked ? 'True' : 'False'

    }
    handleRelatedModelChange(value) {
        this.state.edited = true
        this.state.related_model = value;
    }
    async attrDomain(ev) {
        this.state.edited = true
        const parent = event.target.closest('.cy-basedOn')
        var attribute = parent.getAttribute('data-attribute')
        var domain = '';
        if (attribute === 'readonly' && this.state.item_name?.props.fieldInfo.readonly) {
            domain = this.state.readonly ? this.state.readonly : this.state.item_name.props.fieldInfo.readonly
        } else if (attribute === 'invisible' && this.state.item_name?.props.fieldInfo.invisible) {
            domain = this.state.invisible ? this.state.invisible : this.state.item_name.props.fieldInfo.invisible
        } else if (attribute === 'required' && this.state.item_name?.props.fieldInfo.required) {
            domain = this.state.required ? this.state.required : this.state.item_name.props.fieldInfo.required
        } else {
            domain = false
        }
        var resModel = this.action.currentController.props.resModel
        var fields_detail = await this.orm.searchRead("ir.model.fields", [
            ["model", "=", resModel]
        ])

        domain = domain ? domain : "False";
        const fieldsDict = {};
        fields_detail.forEach(field => {
            const fieldName = field.name;
            fieldsDict[fieldName] = field;
        });
        var fields_info = fieldsDict;
        this.addDialog(ExpressionEditorDialog, {
            resModel,
            fields: fields_info,
            expression: domain,
            onConfirm: (expression) => this.modifier(expression, attribute),
        });
    }
    modifier(expression, attribute) {
        this.attribute = attribute
        if (attribute == 'invisible') {
            this.state.invisible = expression
        }
        if (attribute == 'readonly') {
            this.state.readonly = expression
        }
        if (attribute == 'required') {
            this.state.required = expression
        }
    }
    get newFieldWidgets() {
        return this.state.widget_types.length ? [{
            value: false,
            label: ''
        }, ...this.state.widget_types] : this.state.widget_types
    }

    FieldTypeChange(value) {
        if (value === 'button') {
            this.createButton();
        } else if (value === 'new') {
            this.createNewField();
        } else if (value === 'existing') {
            this.env.bus.trigger("LIST_EXISTING_FIELDS", {
                name: "ExistingName",
                type: "ExistingProperties",
            });
            this.env.bus.trigger('CLEAR-MENU');
        }
    }

    async createButton() {

        this.env.bus.trigger("BUTTON_DETAILS", {
            type: "ButtonProperties",
            path: "/tree",
            position: "inside",
        });
    }



    handleFieldWidgetChange(value) {
        this.state.widget = value;
        this.widgetOptionalFields(this.state.widget)
    }


    //    Widget Options Start
    widgetOptionalFields(widget_name, widget_options = null) {
        if (document.getElementById('dynamic-container')) {
            document.getElementById('dynamic-container').innerHTML = '';
        }
        if (widget_name) {

            if (widget_name == "statusbar") {
                this.state.isStatusBar = true
            } else {
                this.state.isStatusBar = false
            }
            const supportedOptions = getWidgetSupport(widget_name);
            const widgetOption = getWidgetTypes(widget_name)
            console.log("fsff", supportedOptions)
            console.log("fsff", widgetOption)
            if (supportedOptions) {
                const container = document.getElementById('dynamic-container');
                if (container) {
                    container.innerHTML = '';
                    supportedOptions.forEach(async field => {
                        console.log("gdhj", field)
                        const fieldName = field.options.name;
                        const widgetOptionsType = widgetOption.component?.props[fieldName]?.type
                        let widgetOptionsType_value = "";

                        if (widgetOptionsType) {
                            widgetOptionsType_value = widgetOptionsType.name.toString();
                        }
                        var fieldValue = this.state.item_name?.props.fieldInfo.options[fieldName] || ''
                        if (field.options.availableTypes && field.options.availableTypes.length > 0) {
                            const optionFields = this.state.field_type === 'many2many' ? this.state.related_model : this.existingFields
                            if (optionFields) {
                                this.state.charFields = Object.keys(optionFields)
                                    .filter(key => optionFields[key].type === field.options.availableTypes[0])
                                    .reduce((obj, key) => {
                                        obj[key] = optionFields[key];
                                        return obj;
                                    }, {});
                            }
                            //                            const x2manyFields = Object.keys(this.existingFields)
                            //                                .filter(key => this.existingFields[key].type === field.options.availableTypes[0])
                            //                                .reduce((obj, key) => {
                            //                                    obj[key] = this.existingFields[key];
                            //                                    return obj;
                            //                                }, {});


                            if (widget_name === 'monetary') {
                                const options = Object.keys(this.state.charFields)
                                    .filter(item => this.state.charFields[item].relation === 'res.currency')
                                    .reduce((acc, key) => {
                                        acc[key] = this.state.charFields[key];
                                        return acc;
                                    }, {});

                                // Update charFields with the filtered options (for 'monetary' widget)
                                this.state.charFields = options;
                            }
                        }
                        var obj = field.options.label
                        let string = "";
                        for (const key in obj) {
                            if (obj.hasOwnProperty(key)) {
                                string += obj[key];
                            }
                        }
                        if (field.options.type === 'field') {
                            if (fieldName === "fold_field") {
                                const div = document.createElement('div');
                                div.id = fieldName + '_div'; // Use field name as ID
                                div.innerHTML = `
                            <label class="cy-radio_label" for="${fieldName}">
                                <input class="form-check-input " type="checkbox" id="${fieldName}" name="${fieldName}" ${fieldValue ? 'checked' : ''} >
                                ${obj}
                            </label>
                        `;
                                container.appendChild(div);
                            } else {
                                const div = document.createElement('div');
                                div.id = fieldName + '_div'; // Use field name as ID
                                div.innerHTML = `
                            <label class="cy-radio_label" for="${fieldName}">${obj}:</label>
                        `;
                                container.appendChild(div);
                                const div2 = document.createElement('div');
                                div2.setAttribute('id', fieldName);
                                div2.classList.add('cy-studio-custom-dropdown-image-widget')
                                container.appendChild(div2);;
                                console.log("ImgWidgt", this)
                                await owl.mount(CylloStudioDropdown, div2, {
                                    props: {
                                        options: this.ImageWidget,
                                        defaultValue: fieldValue,
                                        onChange: (value) => this.AddModelWidget({
                                            [fieldName]: value
                                        })

                                    },
                                })
                            }
                        } else if (field.options.type === 'string') {
                            const div = document.createElement('div');
                            div.id = fieldName + '_div';

                            // Create label element
                            const label = document.createElement('label');
                            label.className = 'cy-navbar_label';
                            label.htmlFor = fieldName; // Links the label to the input by ID
                            label.textContent = `${obj}:`;

                            // Create input element
                            const input = document.createElement('input');
                            input.className = 'cy-input';
                            input.type = 'text';
                            input.autocomplete = 'off';
                            input.id = fieldName;
                            input.name = fieldName;
                            input.value = fieldValue;
                            if (widgetOptionsType) {
                                input.placeholder = `Expected Input  As :- ${widgetOptionsType_value}`;
                            }

                            // Bind events
                            input.addEventListener('change', (ev) => this.fieldValidation(ev, widgetOptionsType_value)); // Event for the input
                            // Append elements
                            div.appendChild(label);
                            div.appendChild(input);

                            // Append the div to the container
                            container.appendChild(div);
                        } else if (field.options.type == 'boolean') {
                            const div = document.createElement('div');
                            div.id = fieldName + '_div';
                            div.innerHTML = `
                                <label class="cy-radio_label" for="${fieldName}">
                                    <input class="form-check-input" type="checkbox" id="${fieldName}" name="${fieldName}" ${fieldValue ? 'checked' : ''} onClick="(ev)=>onClickColorChangeLabel(ev)">
                                    ${obj}
                                </label>
                            `;
                            div.addEventListener('click', function(ev) {
                                const label = document.getElementsByClassName('cy-radio_label')
                                const checkbox = ev.target;
                                if (checkbox.checked) {
                                    ev.srcElement.parentElement.style.color = '#B9B8C3';
                                } else {
                                    ev.srcElement.parentElement.style.color = "#828176";
                                }
                            })
                            container.appendChild(div);
                        }
                    })
                }

            }
        } else if (document.getElementById('dynamic-container')) {
            const container = document.getElementById('dynamic-container');
            container.innerHTML = '';
        }
    }

    get ImageWidget() {
        const arr = [{
            value: false,
            label: ''
        }]
        for (let value in this.state.charFields) {
            const obj = {
                value: this.state.charFields[value].name,
                label: this.state.charFields[value].string || this.state.charFields[value].display_name
            }
            arr.push(obj)
        }
        return arr
    }

}
FieldProperties.components = {
    CylloStudioDropdown,
};