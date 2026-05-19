/** @odoo-module **/
import { Component, useState,onWillUpdateProps,onRendered } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { FieldProperties } from "@cyllo_studio/js/view_editor/aside_bar/properties/field_properties/field_properties";
import { ButtonProperties } from "@cyllo_studio/js/view_editor/aside_bar/properties/button_properties/button_properties";
import { OverallView } from "@cyllo_studio/js/view_editor/aside_bar/overall_view/overall_view";
import { ExistingFieldProperties } from "@cyllo_studio/js/view_editor/aside_bar/properties/existing_field_properties/existing_field_properties";
import { KanbanFieldProperties } from "@cyllo_studio/js/view_editor/aside_bar/properties/field_properties/kanban_field_details";
import { RibbonProperties } from "@cyllo_studio/js/view_editor/kanban/ribbon_properties";
import { TextProperties } from "@cyllo_studio/js/view_editor/kanban/text_properties";
import { StatusBarButtons } from '@web/views/form/status_bar_buttons/status_bar_buttons';
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { PageProperties } from "@cyllo_studio/js/views/cyllo_form/page/page_properties";
import { SmartButtonProperties } from "@cyllo_studio/js/view_editor/aside_bar/properties/smart_button/smart_button_properties";
import { CylloStudioDropdown } from "@cyllo_studio/js/view_editor/dropdown/CylloStudioDropdown";


export class AsideBar extends Component {
  static template = "cyllo_studio.AsideBar";
  static props = {
    type: { type: String },
    handleView: { type: Function, optional: true },
    updateState: { type: Function, optional: true },
    overall: { type: Object, optional: true },
    viewDetails: { type: Object, optional: true },
    fieldProperties: { type: Object, optional: true },
    kanbanComponent: { type: Object, optional: true },
    noteBookProperties:{ type: Object, optional: true },
    SmartButtonProperties:{ type: Object, optional: true },
    isAnimatingSidebar:{ type: Boolean, optional: true },
    activity_view:{ type: Boolean, optional: true },
    ButtonDetails:{ type: Object, optional: true },
    viewDetails: { type: Object, optional: true },
  };
  setup() {
    this.actionService = useService("action");
    this.action = useService("action");
    this.orm = useService("orm");
    this.state = useState({
      viewProperty: this.props.type,
      type:this.props.type
    });
    onWillUpdateProps((props) => {
       if(props.type){
         this.state.type = props.type
       }
    })
      onRendered(()=>{
            console.log('asd3wdsaxz',this)
             this.props.updateState("editButton", false);
        })
    console.log("OnwillUpdtPrps", this)
  }

  get OverallProps() {
    return {
      ...(this.props.overall || {}),
      ...(this.props.viewDetails || {}),
    };
  }
  get fieldPropertiesProps() {
    console.log("jyf", this)
    return {
      ...(this.props.viewDetails || {}),
      ...(this.props.fieldProperties || {}),
     };
  }
  get KanbanFieldPropertiesProps() {
    console.log("kanbanFIELDPROP ABD RETURN :", {
      'viewDetails':this.props.viewDetails || {},
      'overall':this.props.overall || {},
      'fieldProperties':this.props.fieldProperties || {},
    })
    return {
      ...(this.props.overall || {}),
      ...(this.props.fieldProperties || {}),
      ...(this.props.viewDetails || {}),
    };
  }
  get KanbanComponentProps() {
    return {
      ...(this.props.kanbanComponent || {}),
      viewDetails:{...(this.props.viewDetails || {})},

    };
  }
  async closeSidebar(){
   		this.env.bus.trigger('CLEAR-MENU',{ fromClose: true });
   		this.props.updateState("editButton", true);
   		this.props.updateState("isAnimatingSidebar", true);
   		this.props.updateState("edit", false);
  }
  get noteBookPropertiesProps() {
    return {
      ...(this.props.noteBookProperties || {}),
      viewDetails:{...(this.props.viewDetails || {})},

    };
  }
  get SmartButtonPropertiesProps() {
    return {
      ...(this.props.SmartButtonProperties || {}),
      ...(this.props.overall || {}),
      viewDetails:{...(this.props.viewDetails || {})},

    };
  }
  get ButtonPropertiesProps() {
    console.log("BttnPrprties", this)
    return {
      ...(this.props.ButtonDetails || {}),
      viewDetails:{...(this.props.viewDetails || {})},

    };
  }

  get viewDetails() {
    return { ...(this.props.viewDetails ?? {}) };
  }
  get propsType() {
    return (
      this.props.type === "Properties" || this.props.type === "ButtonProperties" || this.props.type =="ribbon"  || this.props.type =="button" || this.props.type==="text"
    );
  }
  get defaultFieldType() {
        return  'new_field'
  }
    get fieldType() {
        return [{value: 'new_field', label: 'New Field'}, {value: 'existing_field', label: 'Existing Field'},{value: 'button_prop', label: 'Button'}]
    }

    get isTreeNew() {
        return (
            this.props.viewDetails.viewType == "tree" && this.props.fieldProperties.create
        )
    }

  FieldTypeChange(ev){
    console.log('wqdasdasdasd',ev)
    if(ev == 'button_prop'){
      this.state.type = 'ButtonProperties';
    }else if(ev == 'new_field'){
      this.state.type = 'Properties';
    }
  }

}
AsideBar.components = {
  FieldProperties,
  OverallView,
  ButtonProperties,
  ExistingFieldProperties,
  KanbanFieldProperties,
  RibbonProperties,
  TextProperties,
  MultiRecordSelector,
  PageProperties,
  SmartButtonProperties,
  CylloStudioDropdown
};
