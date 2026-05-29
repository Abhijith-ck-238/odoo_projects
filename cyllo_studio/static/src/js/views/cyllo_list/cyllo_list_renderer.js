/** @odoo-module */
import { listView } from "@web/views/list/list_view";
import { onMounted,useRef,useState ,onWillRender} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";


export class CylloListRenderer extends listView.Renderer {
  setup() {

    super.setup();
       this.list_trRef = useRef("list-tr");
       this.rpc = useService('rpc');
       this.action = useService("action");
       this.state = useState({
            ...this.state,
            invisible_session: false
       })
    onWillRender(()=>{
        this.state.invisible_session = sessionStorage.getItem('invisible')
    })
    onMounted(() => {
      this.env.bus.trigger("LIST_DETAILS", {
        mode: this.props.archInfo,
        model: this.env.model.config.resModel,
        viewId: this.env.config.viewId,
        viewType: "tree",
        allFields: this.props.list.fields,
        activeFields: this.props.list.activeFields,
      });
       const self = this
       const treeEl = self.list_trRef.el
       if (self.props.activeActions.type === "view") {
                var drake = dragula([treeEl], {
                    revertOnSpill: true,
                    moves: (el, container, handle) => {
                        if (handle.classList.contains("add-fields") || el.classList.contains('add-fields') || el.classList.contains('o_list_open_form_view') || handle.classList.contains('o_list_open_form_view')) {
                            return false;
                        }
                        return !el.classList.contains('o_list_controller');
                    },
                    accepts: (el, target, source, sibling) => {
                        return sibling
                    }
                }).on('cloned', function (clone, original, type) {
                    clone.style.backgroundColor = '#f8f9e5'
                }).on('drop', async (el, target, source, sibling) => {
                    if(this.state.drop === true){
                            this.env.bus.trigger("CLEAR-MENU");
                    }
                    const view_id = self.env.config.viewId

                    const fieldPath = el.getAttribute('cy-xpath') ? el.getAttribute('cy-xpath') : el.querySelector('.cy-listBtn').getAttribute('cyxpath')
                    const siblingField = sibling.getAttribute('cy-xpath') ? sibling.getAttribute('cy-xpath') : sibling.querySelector('.cy-listBtn') ? sibling.querySelector('.cy-listBtn').getAttribute('cyxpath') : null

                    const sourceField = source.getAttribute('cy-xpath')
                    const path = siblingField || sourceField;
                    const position = siblingField ? 'before' : 'inside';
                    try {
                        const response = await self.rpc("/cyllo_studio/move/tree", {
                            method: 'move_tree',
                            model: self.props.list.model.config.resModel,
                            view_id: self.env.config.viewId,
                            view_type: self.env.config.viewType === 'list' ? 'tree' : self.env.config.viewType,
                            args: [],
                            kwargs: {
                                path,
                                position,
                                fieldPath,
                                viewType: self.env.config.viewType,
                                view_id: view_id ? view_id : null,
                                model: self.props.list.model.config.resModel
                            }
                        })
                        if (response) {
                            let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                            let cleanedStr = response.replace(/\s+/g, ' ').trim();
                            storedArray.push(cleanedStr);
                            sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                            sessionStorage.setItem('ReDO', JSON.stringify([]));
                        }
                    } finally {
                        this.env.services.ui.unblock();
                    }
                    this.action.doAction('studio_reload');
                });
            }


    });
  }
  tableLeave(ev) {
    const elements = document.querySelectorAll(".border-class-list");
    elements.forEach((e) => {
      e.classList.remove("border-class-list");
    });
  }

    getActiveColumns(list) {
        const invisible_session = sessionStorage.getItem('invisible');
        return this.allColumns.filter((col) => {
            if (!invisible_session) {
                if (list.isGrouped && col.widget === "handle") {
                    return false; // no handle column if the list is grouped
                }
                if (col.optional === 'hide') {
                    return false
                }
                if (col.optional && !this.optionalActiveFields[col.name]) {
                    return false;
                }
                if (this.evalColumnInvisible(col.column_invisible)) {
                    return false;
                }
            }
            return true;
        });
    }
  onMouseHover(ev) {
    const elements = document.querySelectorAll(".border-class-list");
    elements.forEach((e) => {
      e.classList.remove("border-class-list");
    });

    const currentElement = ev.target.closest("th") || ev.target.closest("td");
    const headers = ev.target
      .closest("tr")
      .querySelectorAll(currentElement.tagName);
    const colIndex = Array.from(headers).indexOf(currentElement);
    const rows = document.querySelectorAll("tr");
    rows.forEach((row) => {
      let cells = row.querySelectorAll("td");
      cells = cells.length ? cells : row.querySelectorAll("th");
      if (
        cells[colIndex] &&
        parseInt(cells[colIndex].getAttribute("colspan") || 0) <= 1
      ) {
        cells[colIndex].classList.add("border-class-list");
      }
    });
  }
  listFieldDetails(ev,column) {

    const fieldType = this.props.list._config.fields[column.name]?.type || "";
    const relational_fields =  this.props.list._config.fields[column.name]?.relation || "";
    this.env.bus.trigger("FIELDS_DETAILS", {
      mode: column.attrs || {},
      name: column.name || "",
      label: column.label || "",
      widget: column.widget || "",
      options: column.options || "",
      fieldType: fieldType || "",
      context: column?.context || "",
      related_model:relational_fields || "",
      type: "Properties",
      edit:true,
      cy_path:column.attrs["cy-xpath"],
      help: column.help || "",
      placeholder:column.attrs["placeholder"]||"",
      invisible:column.invisible || "" ,
      readonly:column.readonly || "",
      required:column.required ||"",
    });
  }
    itemOnClick(ev) {
        const newth = document.createElement('th');
        const newtd = document.createElement('td');

        newth.setAttribute('data-tooltip-delay', '1000');

        newth.setAttribute('tabindex', '-1');
        newtd.setAttribute('tabindex', '-1');
        newth.setAttribute('data-name', 'tax_id');
        newth.className = 'add-fields align-middle cursor-default o_many2many_tags_cell opacity-trigger-hover';
        newth.style.width = '150px';
        newth.innerHTML = `
            <div class="d-flex">
                <span class="d-block min-w-0 text-truncate flex-grow-1">Select Field</span>
                <i class="d-none fa-angle-down opacity-0 opacity-75-hover"></i>
            </div>
            <span class="o_resize position-absolute top-0 end-0 bottom-0 ps-1 bg-black-25 opacity-0 opacity-50-hover z-index-1"></span>
        `;
        let targetContainer = ev.target.parentElement;
        let specificElement = ev.target
        let parentXpath = '/tree'
        const viewArch = this.env.config.viewArch.attributes
        let truncatedPath = ""
        const path = ev.target.parentElement.parentElement.children[0].getAttribute('cy-xpath');
        if (targetContainer) {
            this.env.bus.trigger("FIELDS_DETAILS", {
                type: "Properties",
                create: true,
                cy_path :'/tree',
            })
        }
    }

  setDefaultColumnWidths() {
    const widths = this.state.columns.map((col) =>
      this.calculateColumnWidth(col)
    );
    const sumOfRelativeWidths = widths
      .filter(({ type }) => type === "relative")
      .reduce((sum, { value }) => sum + value, 0);

    const columnOffset = this.hasSelectors ? 2 : 1;
    widths.forEach(({ type, value }, i) => {
      const headerEl = this.tableRef.el.querySelector(
        `th:nth-child(${i + columnOffset})`
      );
      if (type === "absolute" && headerEl) {
        if (this.isEmpty) {
          headerEl.style.width = value;
        } else {
          headerEl.style.minWidth = value;
        }
      } else if (type === "relative" && this.isEmpty) {
        headerEl.style.width = `${((value / sumOfRelativeWidths) * 100).toFixed(
          2
        )}%`;
      }
    });
  }
}
CylloListRenderer.template = "cyllo_studio.CylloListRenderer";
CylloListRenderer.rowsTemplate = "cyllo_studio.CylloListRenderer.Rows";
CylloListRenderer.recordRowTemplate =
  "cyllo_studio.CylloListRenderer.RecordRow";

CylloListRenderer.components = {
  ...listView.Renderer.components,
};
