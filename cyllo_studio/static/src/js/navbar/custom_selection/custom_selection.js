/** @odoo-module **/
import { Component, useState, onWillUpdateProps } from "@odoo/owl";

export class CustomSelection extends Component {
  setup() {
    this.options = [
      { label: "Primary", value: "btn-primary", color: "#9ea700" },
      { label: "Secondary", value: "btn-secondary", color: "#EEEEEE" },
      { label: "Info", value: "btn-info", color: "#0180A5" },
      { label: "Warning", value: "btn-warning", color: "#9a6b01" },
      { label: "Danger", value: "btn-danger", color: "#dc3545" },
    ];
    this.state = useState({
      showDropdown: false,
      class: [],
      selectedOption: null,
      isLinkStyle: false,
    });

    this.processClass(this.props.defaultClass);

    onWillUpdateProps((nextProps) => {
      this.processClass(nextProps.defaultClass);
    });
  }

  processClass(buttonClass) {
    if (buttonClass) {
      let classArray = buttonClass?.split(" ");
      let classIndex = -1;
      let optionArray = this.options.filter((option) => {
        const linkValue = "text-" + option.value.split("-")[1];
        const isLink =
          classArray.includes("btn-link") || classArray.includes(linkValue);
        let index = -1;
        if (
          classArray.includes(option.value) &&
          !classArray.includes("btn-link")
        ) {
          index = classArray.indexOf(option.value);
          classIndex = index !== -1 ? index : classIndex;
          return true;
        } else if (isLink) {
          index = classArray.indexOf(linkValue);
          classIndex = index !== -1 ? index : classIndex;
          return (
            index !== -1 ||
            (!buttonClass.includes("text-") && option.value === "btn-primary")
          );
        }
      });
      if (optionArray.length === 1) {
        this.state.selectedOption = optionArray[0];
        if (classIndex !== -1) {
          let removedClass = classArray.splice(classIndex, 1)[0];
          this.state.isLinkStyle = removedClass.split("-")[0] !== "btn";
        } else {
          this.state.isLinkStyle = true;
        }
        this.state.class = classArray;
      } else {
        this.state.class = classArray;
        this.state.selectedOption = "";
      }
    }
  }

  handleOptionClick(option) {
    this.state.selectedOption = option;
    this.setShowDropdown(false);
    if (this.state.isLinkStyle) {
      if (!this.state.class.includes("btn-link")) {
        this.state.class.push("btn-link");
      }
      this.state.class.push("text-" + option.value.split("-")[1]);
    } else {
      this.state.class.push(option.value);
    }
    this.props.onChange(this.state.class.join(" "));
  }
  setShowDropdown(val = !this.state.showDropdown) {
    this.state.showDropdown = val;
  }
}

CustomSelection.template = "cyllo_studio.CustomSelection";
