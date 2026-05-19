/** @odoo-module **/
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { ViewSelectionDropDown } from "@cyllo_studio/js/navbar/view_selection_dropdown/view_selection_dropdown";
import { useState, useRef } from "@odoo/owl";
import {FirstPage} from '@cyllo_studio/js/new_app/new_app_templates';


export class CylloNavBar extends NavBar {
  static template = "cyllo_studio.CylloNavBar";
  setup() {
    this.orm = useService("orm");
    this.root = useRef("cy_nav_bar");
    this.action = useService("action");
    this.rpc = useService("rpc");
    this.dialogService = useService("dialog");

    this.state = useState({
      lightMode: false,
    });
    this.viewChange = this.viewChange.bind(this);
  }
  createApp() {
        this.dialogService.add(FirstPage, {
            title: 'Cyllo Studio',
        })
    }

//  async ReportClick(){
//         console.log("dee")
//         const [modelId, viewId] = await this.orm.call("ir.model", "cyllo_get_studio_action_acl", [this.action.currentController.action.res_model, 'ir.actions.report']);
////         this.action.doAction("cyllo_studio.action_view_report_studio");
//        console.log(viewId, modelId,)
////         this.action.doAction({
////             name: 'Report',
////             type: 'ir.actions.act_window',
////             res_model: 'ir.actions.report',
////             views: [[viewId, 'kanban']],
////             target: 'current',
////             context: {
////                 default_model_id: modelId,
////                 search_default_model_id: modelId,
////             },
////         });
//            this.action.doAction({
//            type: "ir.actions.client",
//            tag: "report_view",
//        });
//    }

  ShowMiscellaneousDrop () {
        const menuContainer = this.root.el.querySelector('.cy-nav-Menu-button');
        const menuCard =  this.root.el.querySelector('.cy-miscellaneous_card');
//        menuCard.style.display = 'block';
        const containerRect = menuContainer.getBoundingClientRect();
        const cardRect = menuCard.getBoundingClientRect();
        const spaceToRight = window.innerWidth - containerRect.right;
        const spaceToLeft = containerRect.left;
        menuCard.classList.remove('menu-right');
        menuCard.style.left = '0';
        menuCard.style.right = 'auto';
        menuCard.style.zIndex = 999;
        if (spaceToRight < cardRect.width) {
            menuCard.style.left = 'auto';
            menuCard.style.right = '0';
            menuCard.classList.add('menu-right');
        }
    }
  async ReportClick(){
         const [modelId, viewId] = await this.orm.call("ir.model", "cyllo_get_studio_action_acl", [this.action.currentController.action.res_model, 'ir.actions.report']);
//         this.action.doAction("cyllo_studio.action_view_report_studio");
//         this.action.doAction({
//             name: 'Report',
//             type: 'ir.actions.act_window',
//             res_model: 'ir.actions.report',
//             views: [[viewId, 'kanban']],
//             target: 'current',
//             context: {
//                 default_model_id: modelId,
//                 search_default_model_id: modelId,
//             },
//         });
            this.action.doAction({
            type: "ir.actions.client",
            tag: "report_view",
        });
    }
  handleDarkMode() {
    this.state.lightMode = !this.state.lightMode;
    if (this.state.lightMode) {
      document.body.classList.add("light-studio-mode");
      localStorage.setItem("lightModeStudio", this.state.lightMode);
    } else {
      document.body.classList.remove("light-studio-mode");
      localStorage.removeItem("lightModeStudio");
    }
    this.render();
  }
  async handleEdit() {
    this.props.updateState("edit", true);
    this.props.updateState("editButton", false);
  }
  get viewSelectionProps() {
    return {
      view: this.props.view,
      viewChange: this.viewChange,
    };
  }
  viewChange(attr, value) {
    this.props.updateState(attr, value);
  }
  handleClose() {
    const currentUrl = new URL(window.location.href);
    const studio = currentUrl.searchParams.get("studio");
    if (studio === "1") {
      currentUrl.searchParams.delete("studio");
      history.replaceState(null, "", currentUrl.toString());
    }
    currentUrl.searchParams.set("studio", "");
    window.location.href = currentUrl.toString();
    setTimeout(() => window.location.reload(), 500);
  }
  async undoChange() {
    console.log("okkkkkkkkkkkk",this)
    try {
      const storage = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
      const undoElement = storage.pop();
      let view_type = this.props.viewDetails.viewType
      let view_id =  this.props.viewDetails.viewId
      sessionStorage.setItem('UndoRedo', JSON.stringify(storage));
        const element = document.querySelector('.o_content');
        if (element && element.classList.contains('d-none')){
            view_id = 'search'
            view_id = this.env.searchModel.searchViewId
        }
      if (undoElement) {
        let redoStack = JSON.parse(sessionStorage.getItem('ReDO')) || [];
        redoStack.push(undoElement);
        sessionStorage.setItem('ReDO', JSON.stringify(redoStack));
        let xPaths = false
        const count = (undoElement.match(/<xpath /g) || []).length;
        if(count >=2){
            xPaths= true
        }

                await this.rpc('cyllo_studio/undo_action', {
                    model: this.props.viewDetails.model,
                    view_type: view_type,
                    view_id: view_id,
                    xPaths: xPaths,
                });
            }
        } finally {
            this.action.doAction("studio_reload");
            this.env.bus.trigger('resetProperties')
        }
    }

    async redoChange() {
        try {
          const storage = JSON.parse(sessionStorage.getItem('ReDO')) || [];
          const storage_undo = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
          const redoElement = storage.pop();
          let view_type = this.props.viewDetails.viewType
          let view_id =  this.props.viewDetails.viewId
          sessionStorage.setItem('ReDO', JSON.stringify(storage));
            const element = document.querySelector('.o_content');
            if (element && element.classList.contains('d-none')){
                view_type = 'search'
                view_id = this.env.searchModel.searchViewId
            }
          if (redoElement) {
            let undoStack = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
            undoStack.push(redoElement);
            sessionStorage.setItem('UndoRedo', JSON.stringify(undoStack));

            await this.rpc('cyllo_studio/redo_action', {
              model: this.props.viewDetails.model,
              view_type: view_type,
              view_id: view_id,
              arch: redoElement,
            });
          }
        } finally {
          this.action.doAction("studio_reload");
          this.env.bus.trigger('resetProperties')
        }
  }


}
CylloNavBar.props = {
  edit: { type: Boolean, optional: true },
  view: { type: Boolean, optional: true },
  editButton: { type: Boolean, optional: true },
  viewChanged: { type: Boolean, optional: true },
  updateState: { type: Function, optional: true },
  isAnimatingSidebar: { type: Boolean, optional: true },
  activity_view: { type: Boolean, optional: true },
  viewDetails: { type: Object, optional: true },
};
CylloNavBar.components = {
  ViewSelectionDropDown,
};
