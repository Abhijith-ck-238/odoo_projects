/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { SearchBarMenu } from "@web/search/search_bar_menu/search_bar_menu";
import { patch } from "@web/core/utils/patch";
import { Domain } from "@web/core/domain";
import { _t } from "@web/core/l10n/translation";

export class CustomEquipmentFilterMenu extends Component {
    static template = "custom_equipment.CustomEquipmentFilterMenu";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            acquirersMenuOpen: false,
            currentAcquirersMenuOpen: false,
            previousAcquirersMenuOpen: false,
            employeeName: "",
            employeeNameCurrent: "",
            employeeNamePrevious: "",
            isLoading: false,
        });
    }

    // Toggle methods for different filter menus
    toggleAcquirersMenu() {
        this.state.acquirersMenuOpen = !this.state.acquirersMenuOpen;
        this.state.currentAcquirersMenuOpen = false;
        this.state.previousAcquirersMenuOpen = false;
    }

    toggleCurrentAcquirersMenu() {
        this.state.currentAcquirersMenuOpen = !this.state.currentAcquirersMenuOpen;
        this.state.acquirersMenuOpen = false;
        this.state.previousAcquirersMenuOpen = false;
    }

    togglePreviousAcquirersMenu() {
        this.state.previousAcquirersMenuOpen = !this.state.previousAcquirersMenuOpen;
        this.state.acquirersMenuOpen = false;
        this.state.currentAcquirersMenuOpen = false;
    }

    // Apply filter methods
    async applyAcquirersFilter() {
        if (!this.state.employeeName.trim()) {
            this.notification.add(_t("Please enter an employee name"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        try {
            const recordIds = await this.orm.call(
                "equipment.equipment",
                "get_filter_records",
                [this.state.employeeName]
            );

            if (recordIds && recordIds.length > 0) {
                const domain = new Domain([["id", "in", recordIds]]);
                const filter = {
                    type: "filter",
                    description: _t("Acquirers: %s", this.state.employeeName),
                    domain: domain.toList(),
                    groupId: 1,
                    id: `acquirers_${Date.now()}`,
                    isDefault: false,
                };

                this.props.onApplyFilter(filter);
                this.notification.add(_t("Filter applied successfully"), { type: "success" });
            } else {
                this.notification.add(_t("No records found for this employee"), { type: "info" });
            }

            this.state.acquirersMenuOpen = false;
            this.state.employeeName = "";
        } catch (error) {
            console.error("Error applying acquirers filter:", error);
            this.notification.add(_t("Error applying filter"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async applyCurrentAcquirersFilter() {
        if (!this.state.employeeNameCurrent.trim()) {
            this.notification.add(_t("Please enter an employee name"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        try {
            const recordIds = await this.orm.call(
                "equipment.equipment",
                "get_current_acquirer_filter_records",
                [this.state.employeeNameCurrent]
            );

            if (recordIds && recordIds.length > 0) {
                const domain = new Domain([["id", "in", recordIds]]);
                const filter = {
                    type: "filter",
                    description: _t("Current Acquirers: %s", this.state.employeeNameCurrent),
                    domain: domain.toList(),
                    groupId: 1,
                    id: `current_acquirers_${Date.now()}`,
                    isDefault: false,
                };

                this.props.onApplyFilter(filter);
                this.notification.add(_t("Filter applied successfully"), { type: "success" });
            } else {
                this.notification.add(_t("No records found for this employee"), { type: "info" });
            }

            this.state.currentAcquirersMenuOpen = false;
            this.state.employeeNameCurrent = "";
        } catch (error) {
            console.error("Error applying current acquirers filter:", error);
            this.notification.add(_t("Error applying filter"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    async applyPreviousAcquirersFilter() {
        if (!this.state.employeeNamePrevious.trim()) {
            this.notification.add(_t("Please enter an employee name"), { type: "warning" });
            return;
        }

        this.state.isLoading = true;
        try {
            const recordIds = await this.orm.call(
                "equipment.equipment",
                "get_previous_acquirer_filter_records",
                [this.state.employeeNamePrevious]
            );

            if (recordIds && recordIds.length > 0) {
                const domain = new Domain([["id", "in", recordIds]]);
                const filter = {
                    type: "filter",
                    description: _t("Previous Acquirers: %s", this.state.employeeNamePrevious),
                    domain: domain.toList(),
                    groupId: 1,
                    id: `previous_acquirers_${Date.now()}`,
                    isDefault: false,
                };

                this.props.onApplyFilter(filter);
                this.notification.add(_t("Filter applied successfully"), { type: "success" });
            } else {
                this.notification.add(_t("No records found for this employee"), { type: "info" });
            }

            this.state.previousAcquirersMenuOpen = false;
            this.state.employeeNamePrevious = "";
        } catch (error) {
            console.error("Error applying previous acquirers filter:", error);
            this.notification.add(_t("Error applying filter"), { type: "danger" });
        } finally {
            this.state.isLoading = false;
        }
    }

    // Handle Enter key press
    onKeydown(ev, filterType) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            switch (filterType) {
                case "acquirers":
                    this.applyAcquirersFilter();
                    break;
                case "current":
                    this.applyCurrentAcquirersFilter();
                    break;
                case "previous":
                    this.applyPreviousAcquirersFilter();
                    break;
            }
        }
    }

    closeAllMenus() {
        this.state.acquirersMenuOpen = false;
        this.state.currentAcquirersMenuOpen = false;
        this.state.previousAcquirersMenuOpen = false;
    }
}

// Patch the SearchBarMenu to include our custom filters for equipment model
patch(SearchBarMenu.prototype, {
    setup() {
        super.setup();
        this.isEquipmentModel = this.env.searchModel?.resModel === "equipment.equipment";
    },

    /**
     * Apply custom filter to the search model
     * @param {Object} filter - Filter object to apply
     */
    applyCustomFilter(filter) {
        if (this.env.searchModel) {
            // Add the filter to the search model
            this.env.searchModel.addAutoCompletionValues(filter.groupId, [filter]);
            this.env.searchModel.toggleFilter(filter.id);
        }
    }
});

// Register the component
CustomEquipmentFilterMenu.components = {};