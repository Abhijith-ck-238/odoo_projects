/** @odoo-module **/
import { Layout } from "@web/search/layout";
import { onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SearchView } from "@cyllo_studio/js/views/cyllo_search/search_view";
import { patch } from "@web/core/utils/patch";

patch(Layout.prototype, {
  setup() {
    super.setup();
    this.rpc = useService("rpc");
    this.action = useService("action");
    this.state = useState({
      ...this.state,
      isSearchView: false,
      newClick: false,
    });
    onWillStart(() => {
      const cyStudioSearch =
        JSON.parse(sessionStorage.getItem("cyStudioSearch")) || false;
      if (cyStudioSearch) {
        if (cyStudioSearch?.viewId === this.env.searchModel.searchViewId) {
          this.state.isSearchView = cyStudioSearch?.show || false;
        } else {
          sessionStorage.removeItem("cyStudioSearch");
        }
      }
    });
    this.env.bus.addEventListener("SEARCH_CLICKED", async (ev) => {
      console.log("SEARCH_CLICKED");
      this.toggleSearchView();
    });
  },
  async toggleSearchView() {
    console.log("toggleSearchView", this);
    if (!this.state.isSearchView) {
      let searchViewId = this.env.searchModel.searchViewId;
      if (!searchViewId) {
        await this.createSearchView();
      } else {
        this.setSearchSession(searchViewId);
        this.state.isSearchView = !this.state.isSearchView;
      }
    }
  },
  setSearchSession(searchViewId) {
    const cyStudioSearch = JSON.stringify({
      viewId: searchViewId,
      show: !this.state.isSearchView,
    });
    sessionStorage.setItem("cyStudioSearch", cyStudioSearch);
  },
  get searchView() {
    return SearchView;
  },
  async createSearchView() {
    this.env.services.ui.block();
    console.log("createSearchView", this);
    try {
      let searchViewId = await this.rpc("cyllo_studio/search/add/search_view", {
        arch: this.env.searchModel.searchViewArch,
        model: this.env.searchModel.resModel,
      });
      this.setSearchSession(searchViewId);
    } finally {
      this.env.services.ui.unblock();
    }
    this.action.doAction("studio_reload");
  },
});
Layout.template = "studio.CylloLayout";
Layout.components = {
  ...Layout.components,
  SearchView,
};
Layout.props = {
  ...Layout.props,
  type: {
    type: String,
    optional: true,
  },
  model: {
    type: String,
    optional: true,
  },
};
