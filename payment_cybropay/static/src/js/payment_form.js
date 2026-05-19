/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { rpc } from "@web/core/network/rpc";
import { PaymentForm } from "@payment/interactions/payment_form";

patch(PaymentForm.prototype, {
    async _prepareInlineForm(providerId, providerCode, paymentOptionId, paymentMethodCode, flow) {
        if (providerCode !== 'cybropay_direct') {
            await super._prepareInlineForm(...arguments);
            return;
        } else if (flow === 'token') {
            return;
        }
        this._setPaymentFlow('direct');
    },

    async _processDirectFlow(providerCode, paymentOptionId, paymentMethodCode, processingValues) {
        if (providerCode !== 'cybropay_direct') {
            await super._processDirectFlow(...arguments);
            return;
        }

        const simulatedState = document.getElementById('cybropay_simulated_state')?.value || 'done';

        rpc('/payment/cybropay/direct/simulate_payment', {
            'reference': processingValues.reference,
            'simulated_state': simulatedState,
        }).then(() => {
            window.location = '/payment/status';
        }).catch((error) => {
            this._displayErrorDialog("Payment processing failed", error.message);
            this._enableButton();
        });
    },
});
