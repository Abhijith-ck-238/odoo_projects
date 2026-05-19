/** @odoo-module **/
import { FormLabel } from "@web/views/form/form_label";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";

patch(FormLabel.prototype, {
  async setup() {
    super.setup();
//    this.content = registry.category("cyllo_studio_widget_list").get("widget_list")
  },
  onItemClick(e) {
    let parent = e.target.closest(".o_wrap_field");
    let item_path = parent?.firstElementChild.getAttribute("cy-xpath") || "";
    let has_multipath = false;
    if (!item_path) {
      let child = parent?.firstElementChild;
      if (child?.firstElementChild.nodeName == "BUTTON") {
        item_path = child?.firstElementChild.getAttribute("cy-xpath");
      } else {
        has_multipath = true;
        item_path = {
          first_path: child?.firstElementChild.getAttribute("cy-xpath"),
          second_path:
            child?.nextElementSibling?.firstElementChild.getAttribute("cy-xpath"),
        };
      }
    }

     const allIcons = document.querySelectorAll('.cy-studio-field-icons');
    allIcons.forEach(icon => {
        icon.style.opacity = '0';
        icon.style.marginRight = '';
            icon.style.background = '';

    });
    const panelIcons = e.target.parentElement.classList.contains('o_td_label') ? e.target.parentElement.offsetParent.nextElementSibling.querySelector('.cy-studio-field-icons') : e.target.parentElement.nextElementSibling?.querySelector('.cy-studio-field-icons')
    if(panelIcons){
       panelIcons.style.opacity = '1';
        panelIcons.style.marginRight = '0px';
          panelIcons.style.backgroundColor = '#f6fce5';

    }
    const elements = document.querySelectorAll(".border-class");
    elements.forEach((e) => {
      e.classList.remove("border-class");
    });

    let oWrapElement = e.target.closest(".o_wrap_label");
    oWrapElement?.classList.add("border-class");
    oWrapElement?.nextElementSibling.classList?.add("border-class");
    //        oWrapElement.nextElementSibling.classList?.add('border')
    //        oWrapElement.previousElementSibling.classList?.add('border')

    e.preventDefault();
    e.stopPropagation();
    var self = this;
    const targetElement = e.target.parentElement;
    const parentDiv = targetElement.closest(".o_wrap_field");
    if (parentDiv) {
      this.field_name = parentDiv.querySelector(".o_field_widget")?.getAttribute("name");
      const FieldItem = [this.__owl__.children];
      FieldItem.filter(function (item) {
        Object.values(item).filter(function (data) {
          if (data.props && data.props.name === self.field_name) {
            self.item_name = data;
          }
        });
      });
      this.env.bus.trigger("itemFieldName", {
        itemName: this,
        path: this.props.fieldInfo.MainPath,
        widgets:  this.content,
        FieldInfo: this.props.fieldInfo,
        activeFields: this.env.model.config.activeFields,
        item_path: item_path,
        has_multipath: has_multipath,
      });
    }
  },
});

FormLabel.props = {
  ...FormLabel.props,
  cyXpath: { type: String, optional: true },
};

FormLabel.template = "cyllo_studio.FormLabel";
