/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { AccountPaymentField } from "@account/components/account_payment_field/account_payment_field";
import { DateTimeInput } from "@web/core/datetime/datetime_input";
const { DateTime } = luxon;

patch(AccountPaymentField.prototype, {

    getInfo() {
        // ✅ call parent
        const result = super.getInfo();
        const invoice_date =DateTime.fromISO(this.props.record.data.date);
        console.log("invoice_date",invoice_date)
        const LIMIT_ID = DateTime.fromISO("2026-01-15");
        console.log("LIMIT_ID",LIMIT_ID)
        for (const line of result.lines) {
            console.log("line before", line);
            if (invoice_date && invoice_date < LIMIT_ID) {
                console.log("if state")
                line.amount_formatted = line.amount_company_currency;
            }
        }

        return result;
    }
});
