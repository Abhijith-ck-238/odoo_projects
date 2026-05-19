/** @odoo-module **/
import { AnalyticDistribution } from "@analytic/components/analytic_distribution/analytic_distribution";
import { patch } from "@web/core/utils/patch";
import { _t } from "@web/core/l10n/translation";

patch(AnalyticDistribution.prototype, {
   setup() {
       super.setup();
   },
   recordProps(line) {
       const resModel = this.props.record._config.resModel;
       if (resModel !== 'hr.expense.budget.policy') {
       return super.recordProps(line);
       }

       const analyticAccountFields = {
           id: { type: "int" },
           display_name: { type: "char" },
           color: { type: "int" },
           plan_id: { type: "many2one" },
           root_plan_id: { type: "many2one" },
       };

       const recordFields = {};
       const values = {};

       // Domain from selected plans
       const selectedPlanIds = Array.from(
           this.props.record.data.scope_analytic_plan_ids?.currentIds || []
       );

       // one analytic account field only
       recordFields["analytic_account_id"] = {
           string: _t("Analytic Account"),
           relation: "account.analytic.account",
           type: "many2one",
           related: {
               fields: analyticAccountFields,
               activeFields: analyticAccountFields,
           },
           domain: [["root_plan_id", "in", selectedPlanIds]],
       };

       let accountValue = false;
        if (line && line.analyticAccounts && Array.isArray(line.analyticAccounts)) {

           // Find the entry that has an accountId (not just plan info)
           const accountEntry = line.analyticAccounts.find(entry =>
               entry.accountId !== undefined && entry.accountId !== null
           );

           if (accountEntry) {
               const accountId = accountEntry.accountId;
               const accountName = accountEntry.accountDisplayName || "";

               if (accountId) {
                   accountValue = [accountId, accountName];
               }
           }
       }
       values["analytic_account_id"] = accountValue;
       //  Percentage field
       recordFields["percentage"] = {
           string: _t("Percentage"),
           type: "percentage",
           cellClass: "numeric_column_width",
           ...this.decimalPrecision,
       };
       values["percentage"] = line?.percentage || 0;
       return {
           fields: recordFields,
           values,
           activeFields: recordFields,
           onRecordChanged: async (record, changes) =>
               await this.lineChanged(record, changes, line),
       };
   },

   async lineChanged(record, changes, line) {
        const resModel = this.props.record._config.resModel;
       if (resModel !== 'hr.expense.budget.policy') {
       return super.lineChanged(record, changes, line);
   }
     const selected = record.data?.analytic_account_id;
       if ("analytic_account_id" in changes) {
           if (Array.isArray(selected) && selected.length >= 2) {
               const [accountId, accountDisplayName] = selected;

               // Update the line's analyticAccounts array
               line.analyticAccounts = [{
                   accountId: accountId,
                   accountDisplayName: accountDisplayName,
                   accountColor: 0,
                   accountRootPlanId: accountId,
               }];
           } else if (selected === false || selected === null || selected === undefined) {
               line.analyticAccounts = [];
           }
       }
       // Handle percentage changes
       if ("percentage" in changes) {
           line.percentage = record.data.percentage || 100;
       }
   }
});
