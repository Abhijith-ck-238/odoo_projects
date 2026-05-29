from odoo import models

class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'
    
    def _get_specific_rendering_values(self, processing_values):
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'cybropay': return res
        return {
            'api_url': '/payment/cybropay/simulate_payment',
            'reference': self.reference,
        }
        
    def _extract_amount_data(self, payment_data):
        if self.provider_code in ('cybropay', 'cybropay_direct'):
            return None
        return super()._extract_amount_data(payment_data)

    def _apply_updates(self, payment_data):
        super()._apply_updates(payment_data)
        if self.provider_code not in ('cybropay', 'cybropay_direct'): return
        status = payment_data.get('status')
        if status == 'done': self._set_done()
        elif status == 'cancel': self._set_canceled()
