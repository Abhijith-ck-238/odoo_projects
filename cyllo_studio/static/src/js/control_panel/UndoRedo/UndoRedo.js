/** @odoo-module **/
import { Component, onWillStart, onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class UndoRedo extends Component {
  static template = "cyllo_studio.UndoRedo";

  setup() {
    this.rpc = useService("rpc");
    this.action = useService("action");
    this.state = useState({
        undo : false,
        redo : false
    })
    onMounted(()=>{
       let UndoRedo = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
        let redo = JSON.parse(sessionStorage.getItem('ReDO')) || [];
       if(UndoRedo.length > 0){
            this.state.undo = true
       }
        if(redo.length > 0){
            this.state.redo = true
       }

    });
  }

  async undoChange() {
    try {
      const storage = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
      const undoElement = storage.pop();
      let view_type = this.env.config.viewType
      let view_id =  this.env.config?.viewId
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
                    model: this.props.model,
                    view_type: view_type,
                    view_id: view_id,
                    xPaths: xPaths,
                });
            }
        } finally {
            this.action.doAction("studio_reload");
//            this.env.bus.trigger('resetProperties')
        }
    }

  async redoChange() {
    try {
      const storage = JSON.parse(sessionStorage.getItem('ReDO')) || [];
      const storage_undo = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
      const redoElement = storage.pop();
       let view_type = this.env.config.viewType
      let view_id =  this.env.config?.viewId
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
          model: this.props.model,
          view_type: view_type,
          view_id: view_id,
          arch: redoElement,
        });
      }
    } finally {
      this.action.doAction("studio_reload");
//      this.env.bus.trigger('resetProperties')
    }
  }
}
