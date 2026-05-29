from odoo import http
from odoo.http import request

class CybroPayController(http.Controller):
    @http.route('/payment/cybropay/direct/simulate_payment', type='jsonrpc', auth='public')
    def cybropay_direct_simulate_payment(self, **data):
        payment_data = {
            'reference': data.get('reference'),
            'status': data.get('simulated_state', 'done'),
        }
        request.env['payment.transaction'].sudo()._process('cybropay_direct', payment_data)

    @http.route('/payment/cybropay/simulate_payment', type='http', auth='public', methods=['POST'], csrf=False)
    def cybropay_simulate_payment(self, **data):
        payment_data = {
            'reference': data.get('reference'),
            'status': data.get('status', 'done'),
        }
        request.env['payment.transaction'].sudo()._process('cybropay', payment_data)
        return request.redirect('/payment/status')
