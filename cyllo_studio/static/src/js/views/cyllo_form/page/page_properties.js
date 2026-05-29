/** @odoo-module **/
import {
  Component,
  useState,
  onWillStart,
  onWillUpdateProps,
  useExternalListener,
  onWillUnmount,
} from "@odoo/owl";
import { useService, useOwnedDialogs } from "@web/core/utils/hooks";
import { MultiRecordSelector } from "@web/core/record_selectors/multi_record_selector";
import { ExpressionEditorDialog } from "@web/core/expression_editor_dialog/expression_editor_dialog";
import {_t} from "@web/core/l10n/translation";
import { handleUndoRedo } from "@cyllo_studio/js/utils/undo_redo_utils";


export class PageProperties extends Component {
  setup() {
    console.log("aaaaa",this)
    const self = this;
    this.rpc = useService("rpc");
    this.action = useService("action");
    this.addDialog = useOwnedDialogs();
    this.notification = useService("effect");
    this.state = useState({
      pageProperties: this.props.properties,
      group_ids: [],
    });
    onWillUpdateProps((nextProps) => {
      this.state.pageProperties = nextProps.properties;
        });
    }
//    onWillStart(
////      async () => await this.findGroupIds(this.props.pageProperties.groups)
//    );

//    onWillUpdateProps(async (nextProps) => {
////      this.state.pageProperties = nextProps.properties;
//    });

//
//  async findGroupIds(groups) {
//    if (groups) {
//      this.state.group_ids = await this.rpc("cyllo_studio/find/groups", {
//         groups: groups,
//      });
//    }
//  }

  onDomainRadioClick({ target }) {
     console.log("asfadfadfdafdsf",this.state)
//    const autofocusIsAdded = this.props.pageProperties?.autofocus ? true : false
//     if(!autofocusIsAdded && this.props.autofocus && target.id === 'autofocus'){
//        this.notification.add({
//            title: _t("Action cannot be performed"),
//            message: "Already AutoFocus Been Used.",
//            type: "notification_panel",
//            notificationType: "warning",
//        });
//        target.checked=false
//    }
//    else{
    if (target.name == "autofocus") {

         this.state.pageProperties[target.name]  = this.state.pageProperties[target.name]? "": "autofocus";
    }
    else {
      this.state.pageProperties[target.name] = target.checked ? "True" : "False";
    }


  }

//  pageInvisibleDomain() {
//    var resModel = this.action.currentController.props.resModel;
//    this.addDialog(ExpressionEditorDialog, {
//      resModel,
//      fields: this.props.fields,
//      expression: this.state.pageProperties.invisible,
//      onConfirm: (domain) => (this.state.pageProperties.invisible = domain),
//    });
//  }

  async updatePage() {
    const view_id = this.props.viewDetails.viewId;
    console.log("update_page",this.state.pageProperties)
//     let not_present_path
//        let has_sheet_group = true
//        const sheet = document.querySelector('.o_form_sheet')
//        if(sheet?.querySelector('.o_group')?.querySelector('.o_inner_group')) {
//            not_present_path = sheet?.querySelector('.o_group')?.querySelector('.o_inner_group').getAttribute('cy-xpath')
//        } else if (sheet?.querySelector('.o_group')) {
//            not_present_path = sheet?.querySelector('.o_group')?.getAttribute('cy-xpath')
//        } else {
//            has_sheet_group = false
//            not_present_path = sheet?.getAttribute('cy-xpath')
//        }
//        has_sheet_group = !!sheet?.querySelector('.o_group')
//            console.log(has_sheet_group,'llllllllll',this.props)
    //@error invisible domain with not existing field
   const response = await this.rpc("cyllo_studio/update/page", {
      method: "update_page",
      model: this.props.viewDetails.model,
      view_id: this.props.viewDetails.viewId,
      view_type: "form",
      args: [],
      kwargs: {
        view_id: view_id ? view_id : null,
        model: this.action.currentController.props.resModel,
        path: this.state.pageProperties.cyXpath,
        string: this.state.pageProperties.title,
        autofocus: this.state.pageProperties.autofocus ||'',
        invisible: this.state.pageProperties.invisible ||'',
//        groups: this.state.group_ids,
        viewType: "form",
          active_fields: this.props.viewDetails.activeFields,
//        has_sheet_group,
//        not_present_path,
      },
    });
   if(response){
            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
            let cleanedStr = response.replace(/\s+/g, ' ').trim();
            storedArray.push(cleanedStr)
            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
            sessionStorage.setItem('ReDO', JSON.stringify([]));
    }
    this.env.bus.trigger('resetProperties');
    this.action.doAction("studio_reload");
  }
  async removePage() {
    console.log("asdasdasdasdsaaaaaaaaaaaaaaaaaaaaawwwwww",this.props)
    const view_id = this.props.viewDetails.viewId;
    console.log("view_id",view_id)
    const path =  this.props.properties.cyXpath;
    console.log("232323", path);
    const response = await this.rpc("cyllo_studio/delete/existing_page", {
      method: "delete_existing_page",
      model: this.props.viewDetails.model,
      view_id: this.props.viewDetails.viewId,
      view_type: this.props.viewDetails.viewType,
      args: [
        {
          path: path ? path : this.props.properties.cyXpath,
          pageName: this.props.properties.title,
          model: this.action.currentController.action.res_model,
        },
      ],
//      kwargs: { view_id: this.props.viewDetails},
      kwargs: { view_id:this.props.viewDetails.viewId},
    });
       if(response){
            handleUndoRedo(response);

        }
    this.action.doAction("studio_reload");
    this.env.bus.trigger("CLEAR-MENU");
  }

}

PageProperties.components = {
  MultiRecordSelector,
};
PageProperties.template = "cyllo_studio.PageProperties";
