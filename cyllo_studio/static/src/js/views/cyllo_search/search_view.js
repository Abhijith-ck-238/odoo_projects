/** @odoo-module **/
import { SearchBarMenu } from "@web/search/search_bar_menu/search_bar_menu";
import { onMounted, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";
import { DomainSelectorDialog } from "@web/core/domain_selector_dialog/domain_selector_dialog";
import { FilterDomainSelectorDialog } from "./dialog/filter_domain_selector_dialog";
import { GroupByDialog } from "./dialog/groupby_dialog";
import { SearchFieldDialog } from "./dialog/search_field_dialog";
import { SearchPanelValueDialog } from "./dialog/search_panel_value_dialog";
import { SearchPanelDialog } from "./dialog/search_panel_dialog";

export class SearchView extends SearchBarMenu {
  static template = "cyllo_studio.SearchView";
  static components = { ...SearchBarMenu.components };

  setup() {
    super.setup();
    this.rpc = useService("rpc");
    this.action = useService("action");
//    onMounted(() => this.onMounted());
    this.filterRef = useRef("filterRef");
    this.groupRef = useRef("groupRef");
    this.searchFieldRef = useRef("searchFieldRef");
    this.searchPanelRef = useRef("searchPanelRef")
    this.searchPanelItems = this.env.searchModel.sections
    this.searchPanelInfo = this.env.searchModel.searchPanelInfo
    this.state = useState({
        ...this.state,
        searchFields: this.env.searchModel.getSearchItems((searchItem) => ["field"].includes(searchItem.type)),
        filterItems: this.env.searchModel.getSearchItems((searchItem) => ["filter", "dateFilter", "filterSeparator"].includes(searchItem.type)),
        groupByItems: this.env.searchModel.getSearchItems((searchItem) => ["groupBy", "dateGroupBy", "groupSeparator"].includes(searchItem.type) && !searchItem.isProperty),
        searchPanelItems: this.searchPanelItems,
    })


  }

//  onMounted() {
//    const self = this;
//    const filter = this.filterRef.el;
//    const group = this.groupRef.el;
//    const searchField = this.searchFieldRef.el;
//    const searchPanel = this.searchPanelRef.el;
//    var drake = dragula([filter, group, searchField,searchPanel], {
//      revertOnSpill: true,
//      moves: function (el, container, handle) {
//        if (handle.classList.contains("handle-drag")) {
//              return true;
//        }
//        return false
//      },
//      accepts: function (el, target, source, sibling) {
//        if (target === source) {
//          return true;
//        }
//        return false;
//      },
//    }).on("drop", async function (el, target, source, sibling) {
//      let path = el.getAttribute("cy-xpath");
//      const nextSiblingPath = sibling?.getAttribute("cy-xpath") || null;
//
//      const sibling_path =
//        nextSiblingPath || el.previousElementSibling.getAttribute("cy-xpath");
//      const position = nextSiblingPath ? "before" : "after";
//      self.env.services.ui.block();
//      try {
//       const response =  await self.rpc("cyllo_studio/search/move/item", {
//          view_id: self.env.searchModel.searchViewId,
//          model: self.env.searchModel.resModel,
//          path,
//          position,
//          sibling_path,
//        });
//         if(response){
//                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
//                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
//                    storedArray.push(cleanedStr);
//                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
//                    sessionStorage.setItem('ReDO', JSON.stringify([]));
//                }
//      } finally {
//        self.env.services.ui.unblock();
//      }
//      self.action.doAction("studio_reload");
//    });
//  }

  get sampleValues(){
    return ['Customer', 'Sales Team', 'Create Date']
  }

  get searchFields() {
    return this.state.searchFields
  }

  get groupByItems() {
    return this.env.searchModel.getSearchItems(
      (searchItem) =>
        ["groupBy", "dateGroupBy", "groupSeparator"].includes(
          searchItem.type
        ) && !searchItem.isProperty
    );
  }

  get filterItems() {
    return this.state.filterItems
  }

  async addSeperator(sibling) {
    this.env.services.ui.block();
    try {
      const response = await this.rpc("cyllo_studio/search/add/separator", {
        sibling_path: sibling.cyXpath,
        view_id: this.env.searchModel.searchViewId,
        model: this.env.searchModel.resModel,
      });
       if(response){
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
    } finally {
      this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
  }

  async addFilter(sibling) {
    const { domainEvalContext: context, resModel } = this.env.searchModel;
    const domain = await this.getDefaultLeafDomain(resModel);
    let path = sibling?.cyXpath || this.searchPanelInfo?.filter || "/search";

    this.dialogService.add(FilterDomainSelectorDialog, {
      resModel,
      defaultConnector: "|",
      domain,
      context,
      allFields: this.env.searchModel.searchViewFields,
      onConfirm: async (properties) =>
        await this.saveFilter(path, properties),
      title: _t("Add New Filter"),
      confirmButtonText: _t("Add"),
      discardButtonText: _t("Cancel"),
      isDebugMode: this.env.searchModel.isDebugMode,
    });
  }

  async addGroupBy(sibling) {
    this.dialogService.add(GroupByDialog, {
      fields: this.fields,
      allFields: this.env.searchModel.searchViewFields,
      path: sibling?.cyXpath || this.searchPanelInfo?.groupBy || "/search",
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
    });
  }

  addSearchField(sibling) {
    this.dialogService.add(SearchFieldDialog, {
      fields: this.fields,
      allFields: this.env.searchModel.searchViewFields,
      path: sibling?.cyXpath || "/search",
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
    });
  }

  async editSearchField(item) {
    let properties = {
      string: item.description || "",
      field: item.fieldName,
      invisible: item.invisible || "false",
      groupIds: [],
    };
    if (item.groups) {
      properties.groupIds = await this.rpc("cyllo_studio/find/groups", {
        groups: item.groups,
      });
    }
    this.dialogService.add(SearchFieldDialog, {
      fields: this.fields,
      allFields: this.env.searchModel.searchViewFields,
      path: item.cyXpath,
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
      properties,
    });
  }

  async editFilter(item) {
    let properties = {
      label: item.description || "",
      invisible: item.invisible || "false",
      groupIds: [],
    };
    if(item.type === "dateFilter"){
      properties.fieldName = item.fieldName
      properties.defaultValues = item.defaultGeneratorIds
    }
    if (item.groups) {
      properties.groupIds = await this.rpc("cyllo_studio/find/groups", {
        groups: item.groups,
      });
    }
    const { domainEvalContext: context, resModel } = this.env.searchModel;
    this.dialogService.add(FilterDomainSelectorDialog, {
      resModel,
      defaultConnector: "|",
      domain: item.domain || "",
      context,
      properties,
      allFields: this.env.searchModel.searchViewFields,
      onConfirm: async (properties) =>
        await this.updateFilter(item.cyXpath, properties),
      title: _t("Update Filter"),
      confirmButtonText: _t("Update"),
      discardButtonText: _t("Cancel"),
      isDebugMode: this.env.searchModel.isDebugMode,
    });
  }

  async updateFilter(path, properties) {
    this.env.services.ui.block();
    try {
     const response =  await this.rpc("cyllo_studio/search/update/filter", {
        path,
        properties,
        view_id: this.env.searchModel.searchViewId,
        model: this.env.searchModel.resModel,
      });
       if(response){
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
    } finally {
      this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
  }

  async saveFilter(sibling_path, properties) {
    this.env.services.ui.block();
    try {
      const response = await this.rpc("cyllo_studio/search/add/filter", {
        sibling_path,
        properties,
        view_id: this.env.searchModel.searchViewId,
        model: this.env.searchModel.resModel,
      });
       if(response){
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
    } finally {
      this.env.services.ui.unblock();
    }
//    this.action.doAction("studio_reload");
        window.location.reload()
  }


  async editGroupBy(item) {
    let properties = {
      string: item.description || "",
      field: item.fieldName,
      invisible: item.invisible || "false",
      groupIds: [],
    };
    if (item.groups) {
      properties.groupIds = await this.rpc("cyllo_studio/find/groups", {
        groups: item.groups,
      });
    }
    this.dialogService.add(GroupByDialog, {
      fields: this.fields,
      allFields: this.env.searchModel.searchViewFields,
      path: item.cyXpath,
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
      properties,
    });
  }

 standardize_color(str){
    var ctx = document.createElement('canvas').getContext('2d');
    ctx.fillStyle = str;
    return ctx.fillStyle;
}


  async SearchPanelValue(item=false) {
     let properties = false
     if (item){
        let color = "#7e8600"
        if(item.color){
            color = item.color.startsWith("#") ? item.color : this.standardize_color(item.color)
         }
        properties = {
          string: item.description || "",
          field: item.fieldName,
          icon: item.icon || "",
          color: color,
          hierarchize: item.hierarchize,
          enable_counters: item.enableCounters,
          expand: item.expand,
          limit: item.limit,
          select: item.type === 'category' ? 'one' : 'multi',
          invisible: item.invisible || "False",
          groupIds: [],
        };
        if (item.accessGroups) {
          properties.groupIds = await this.rpc("cyllo_studio/find/groups", {
            groups: item.accessGroups,
          });
        }
     }

    this.dialogService.add(SearchPanelValueDialog, {
      fields: this.fields,
      allFields: this.env.searchModel.searchViewFields,
      path: item ? item.cyXpath : this.searchPanelInfo.cyXpath,
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
      properties,
    });
  }

  async removeItem(path) {
      this.state.searchFields = this.state.searchFields.filter((item) => item.cyXpath !== path)
      this.state.filterItems = this.state.filterItems.filter((item) => item.cyXpath !== path)
      this.state.groupByItems = this.state.groupByItems.filter((item) => item.cyXpath !== path)
      let searchPanelItems = []
      this.state.searchPanelItems.forEach((item) => {
          item.cyXpath !== path ? searchPanelItems.push(item) : null
      })
      this.state.searchPanelItems = searchPanelItems
    // this.env.services.ui.block();
    try {
     const response  =  await this.rpc("cyllo_studio/search/remove/item", {
        path,
        view_id: this.env.searchModel.searchViewId,
        model: this.env.searchModel.resModel,
      });
       if(response){
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
    } finally {
//      this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
  }

  get allViews(){
     const filteredViews = this.env.config.views
    .map(item => item[1])
    .filter(value => value !== "search" && value !== "form");

    return filteredViews.reduce((acc, item) => {
        acc[item] = item;
        return acc;
    }, {})
  }

  async addSearchPanel(){
    this.env.services.ui.block();
    try {
      const response = await this.rpc("cyllo_studio/search/add/search_panel", {
        view_id: this.env.searchModel.searchViewId,
        model: this.env.searchModel.resModel,
      });
       if(response){
                    let storedArray = JSON.parse(sessionStorage.getItem('UndoRedo')) || [];
                    let cleanedStr = response.replace(/\s+/g, ' ').trim();
                    storedArray.push(cleanedStr);
                    sessionStorage.setItem('UndoRedo', JSON.stringify(storedArray));
                    sessionStorage.setItem('ReDO', JSON.stringify([]));
                }
    } finally {
      this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
  }

  async editSearchPanel(){
    let groupIds = []
     if (this.searchPanelInfo.groups) {
          groupIds = await this.rpc("cyllo_studio/find/groups", {
            groups: this.searchPanelInfo.groups,
          });
     }
     this.dialogService.add(SearchPanelDialog, {
      path: this.searchPanelInfo.cyXpath,
      viewId: this.env.searchModel.searchViewId,
      model: this.env.searchModel.resModel,
       views: this.allViews,
      properties: {
        view_types: this.searchPanelInfo.viewTypes || [],
        groupIds,
      }
    });
  }
}
