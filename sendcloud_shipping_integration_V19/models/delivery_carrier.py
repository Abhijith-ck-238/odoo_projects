# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Abhijith CK (odoo@cybrosys.com)
#
#    This program is under the terms of the Odoo Proprietary License v1.0(OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
import json
import requests
from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError


class DeliveryCarrier(models.Model):
    """Add sendcloud integration to the delivery.carrier."""
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('sendcloud', "Sendcloud")],
        ondelete={'sendcloud': lambda recs: recs.write(
            {'delivery_type': 'fixed', 'fixed_price': 0})},
        help="Delivery Type used for the shipping")
    sendcloud_developer_key = fields.Char(string="Developer Key",
                                          groups="base.group_system",
                                          help="To specify sendcloud developer"
                                               " key")
    sendcloud_developer_password = fields.Char(string="Password",
                                               groups="base.group_system",
                                               help="To specify sendcloud "
                                                    "password")
    sendcloud_service_id = fields.Many2one("shipping.service",
                                           string="Sendcloud service",
                                           help="To specify the shipping "
                                                "service which is used under "
                                                "sendcloud")
    line_ids = fields.One2many("sendcloud.address",
                               "line_id", string="Lines",
                               help="Show Sendcloud account shipping "
                                    "addresses")
    sender_address_id = fields.Many2one("sendcloud.address",
                                        string="Sender Address",
                                        help="To specify the sender address"
                                             " which is used for shipping")

    def action_get_sender_addresses(self):
        """To specify the sender address for the shipping"""
        public_key, private_key = self.get_credentials()
        response = requests.get(
            'https://panel.sendcloud.sc/api/v2/user/addresses/sender',
            auth=(public_key, private_key))
        if response.status_code == 200:
            self.line_ids.unlink()
            vals = [(0, 0, {
                'name': rec['company_name'],
                'sender_address': rec['id'],
                'email': rec['email'],
                'line_id': self.id,
                'country_id': self.env['res.country'].search(
                    [('code', '=', rec["country"])], limit=1).id
            }) for rec in response.json()['sender_addresses']]
            self.write({'line_ids': vals})
        else:
            self.line_ids.unlink()
            raise ValidationError(_(
                "Invalid credentials. Please check your public and private "
                "keys."))

    def action_get_shipping_services(self):
        """To get the available shipping services and its available countries
         under sendcloud"""
        public_key, private_key = self.get_credentials()
        if not self.sender_address_id.sender_address:
            raise UserError(_("Please specify sender address"))
        response = requests.get(
            'https://panel.sendcloud.sc/api/v2/shipping_methods',
            auth=(public_key, private_key),
            params={'sender_address': self.sender_address_id.sender_address})
        if response:
            self.env['shipping.service'].search([]).unlink()
            for rec in response.json()['shipping_methods']:
                shipping_service_obj = self.env['shipping.service'].create({
                    'name': rec['name'],
                    'service': rec['id'], })
                for countries in rec['countries']:
                    country = self.env['res.country'].search(
                        [('code', '=', countries['iso_2'])], limit=1)
                    if country:
                        shipping_service_obj.available_countries_ids = [(
                            4, country.id)]
        else:
            self.env['shipping.service'].search([]).unlink()

    def sendcloud_rate_shipment(self, order):
        """To get sendcloud shipping rate for selected shipping service.
        :param order: sale.order object,
        :return dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message
                       }
                       """
        public_key, private_key = self.get_credentials()
        weight = self.env.context.get('order_weight', None)
        if not self.sender_address_id:
            return self.sendcloud_return_rate(
                success=False, price=0.0,
                error_message="Please specify sender address",
                warning_message=False)
        # To round the weight
        if not weight:
            weight = 1
        if not order.partner_id.country_id:
            return self.sendcloud_return_rate(
                success=False, price=0.0,
                error_message="Please specify customer country",
                warning_message=False)
        if not self.sendcloud_service_id.service:
            return self.sendcloud_return_rate(
                success=False, price=0.0,
                error_message="Please specify Shipping Service",
                warning_message=False)
        try:
            response = requests.get(
                'https://panel.sendcloud.sc/api/v2/shipping-price',
                auth=(public_key, private_key),
                params={'weight': weight, 'weight_unit': 'kilogram',
                        'from_country': self.sender_address_id.country_id.code,
                        'to_country': order.partner_id.country_id.code,
                        'shipping_method_id': self.sendcloud_service_id.service
                        })
            if response.status_code == 401:
                return self.sendcloud_return_rate(
                    success=False, price=0.0,
                    error_message=
                    "Authentication error -- wrong credentials\n",
                    warning_message=False)
            if response.status_code == 200:
                if response.json()[0]['price']:
                    return self.sendcloud_return_rate(
                        success=True, price=response.json()[0]['price'],
                        error_message=False,
                        warning_message=False)
                else:
                    if self.sendcloud_service_id.service == '8':
                        return self.sendcloud_return_rate(
                            success=True, price=0.0,
                            error_message=False,
                            warning_message=False)
                    else:
                        return self.sendcloud_return_rate(
                            success=False, price=0.0,
                            error_message="Sendcloud did not return prices for "
                                          "this destination country or the "
                                          "weight is out of range.",
                            warning_message=False)
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error occurred")

    def sendcloud_send_shipping(self, pickings):
        """Create a parcel in sendcloud account while validate the transfer.
        :param pickings: stock.picking recordset,
        :return list[dict]: [{'exact_price': a float,
                             'tracking_number': tracking number for the parcel
                            }]
        """
        res = []
        public_key, private_key = self.get_credentials()
        for picking in pickings:
            shipping_values = {}
            parcel_items_list = []
            shipping_values['name'] = picking.partner_id.name
            if picking.partner_id.company_name:
                shipping_values["company_name"] = picking.partner_id.company_name
            else:
                shipping_values["company_name"] = picking.partner_id.name
            shipping_values["email"] = picking.partner_id.email
            shipping_values["telephone"] = picking.partner_id.phone
            shipping_values["address"] = picking.partner_id.street
            shipping_values["house_number"] = 0
            shipping_values["city"] = picking.partner_id.city
            shipping_values["country"] = picking.partner_id.country_id.code
            shipping_values["to_state"] = picking.partner_id.state_id.code
            shipping_values["postal_code"] = picking.partner_id.zip
            for line in picking.move_ids:
                parcel_items = {}
                parcel_items["description"] = line.product_id.name
                parcel_items["product_id"] = line.product_id.id
                parcel_items["quantity"] = line.quantity
                parcel_items["weight"] = (line.quantity * line.product_id.
                                          weight)
                parcel_items["value"] = line.product_id.list_price
                parcel_items_list = parcel_items_list + [parcel_items]
            shipping_values["parcel_items"] = parcel_items_list
            shipping_service_dict = {
                "id": self.sendcloud_service_id.service,
                "name": self.sendcloud_service_id.name}
            shipping_values["shipment"] = shipping_service_dict
            shipping_values[
                "sender_address"] = self.sender_address_id.sender_address
            shipping_values["request_label"] = "True"
            try:
                response = requests.post(
                    'https://panel.sendcloud.sc/api/v2/parcels',
                    auth=(public_key, private_key),
                    json={"parcel": shipping_values})
                if response.status_code in [400, 412]:
                    if response.json()['error'][
                        'message'] == 'shipment: "Invalid shipment.id"':
                        raise UserError(_(
                            "Please check that the shipping service available for"
                            " customer country"))
                    raise UserError(_(response.json()['error']['message']))
                shipping_rate = self.sendcloud_rate_shipment(picking.sale_id)
                tracking = response.json()['parcel']['tracking_number']
                picking.sendcloud_parcel_no = response.json()['parcel']['id']
                shipping_data = {'exact_price': shipping_rate['price'],
                                 'tracking_number': tracking}
                res = res + [shipping_data]
            except requests.exceptions.ConnectionError:
                raise Exception("Connection error occurred")
        return res

    def sendcloud_cancel_shipment(self, pickings):
        """To cancel shipment from the sendcloud account if
        the shipping service allowed to cancel the parcel.
         :param pickings: stock.picking recordset,
        """
        public_key, private_key = self.get_credentials()
        for picking in pickings:
            response = requests.post(
                'https://panel.sendcloud.sc/api/v2/parcels/'
                + picking.sendcloud_parcel_no +
                '/cancel', auth=(public_key, private_key))
            if response.status_code == 410:
                picking.message_post(body=_('Shipment #%s has been cancelled',
                                            picking.carrier_tracking_ref))
                picking.write({'carrier_tracking_ref': '',
                               'carrier_price': 0.0,
                               'sendcloud_parcel_no': ''})
            if response.status_code != 410:
                picking.message_post(body=_(
                    'Sendcloud did not Cancel the Shipment #%s ',
                    picking.carrier_tracking_ref))
                raise UserError(_(
                    "Some shipping services can't cancel.Check the cancel policy"))

    def sendcloud_get_tracking_link(self, picking):
        """To get the tracking info
        :param picking: picking object,
        :return : tracking link,
        """
        public_key, private_key = self.get_credentials()
        tracking_urls = []
        for ref in picking.carrier_tracking_ref.split(','):
            response = requests.get(
                'https://panel.sendcloud.sc/api/v2/tracking/'
                + ref.strip(),
                auth=(public_key, private_key))
            if response.status_code == 200:
                res_json = response.json()
                url = res_json.get('sendcloud_tracking_url') or res_json.get('carrier_tracking_url')
                if url:
                    tracking_urls.append((ref.strip(), url))
        if len(tracking_urls) > 1:
            return json.dumps(tracking_urls)
        elif tracking_urls:
            return tracking_urls[0][1]
        return False

    def get_credentials(self):
        """To get the credentials"""
        return self.sendcloud_developer_key, self.sendcloud_developer_password

    def sendcloud_return_rate(self, success, price, error_message,
                              warning_message):
        """Return sendcloud price when get price otherwise return the error
        message."""
        return {'success': success,
                'price': price,
                'error_message': error_message,
                'warning_message': warning_message}
