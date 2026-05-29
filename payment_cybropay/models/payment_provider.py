from odoo import fields, models

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    
    code = fields.Selection(selection_add=[
        ('cybropay', 'CybroPay Online'),
        ('cybropay_direct', 'CybroPay Direct'),
    ], ondelete={'cybropay': 'set default', 'cybropay_direct': 'set default'})
    
    def _get_default_payment_method_codes(self):
        res = super()._get_default_payment_method_codes()
        if self.code == 'cybropay': return {'cybropay'}
        if self.code == 'cybropay_direct': return {'cybropay_direct'}
        return res
