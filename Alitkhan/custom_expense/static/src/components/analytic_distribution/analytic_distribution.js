/** @odoo-module **/

import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(AnalyticDistribution.prototype,  {
    setup() {
        super.setup();
    },
recordProps(line) {
        const analyticAccountFields = {
            id: { type: "int" },
            display_name: { type: "char" },
            color: { type: "int" },
            plan_id: { type: "many2one" },
            root_plan_id: { type: "many2one" },
        };
        let recordFields = {};
        const values = {};
        // Analytic Account fields
        line.analyticAccounts.map((account) => {
            const fieldName = `x_plan${account.planId}_id`;
            recordFields[fieldName] = {
                string: account.planName,
                relation: "account.analytic.account",
                type: "many2one",
                related: {
                    fields: analyticAccountFields,
                    activeFields: analyticAccountFields,
                },
                // company domain might be required here
//                domain: [["root_plan_id", "=", account.planId]],
            };
            values[fieldName] =  account?.accountId || false;
        });
        // Percentage field
        recordFields['percentage'] = {
            string: _t("Percentage"),
            type: "percentage",
            cellClass: "numeric_column_width",
            ...this.decimalPrecision,
        };
        values['percentage'] = line.percentage;
        // Value field copied from original
        if (this.props.amount_field) {
            const { string, name, type, currency_field } = this.props.record.fields[this.props.amount_field];
            recordFields[name] = { string, name, type, currency_field, cellClass: "numeric_column_width" };
            values[name] = this.props.record.data[name] * values['percentage'];
            // Currency field
            if (currency_field) {
                // TODO: check web_read network request
                const { string, name, type, relation } = this.props.record.fields[currency_field];
                recordFields[currency_field] = { name, string, type, relation, invisible: true };
                values[currency_field] = this.props.record.data[currency_field][0];
            }
        }
        return {
            fields: recordFields,
            values: values,
            activeFields: recordFields,
            onRecordChanged: async (record, changes) => await this.lineChanged(record, changes, line),
        }
}
});


