from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class OfferingOfferingInherit(models.Model):
    _inherit = 'offering.offering'
    _description = 'Offering Offering'

    employee_id = fields.Char(string="Offering Member")
    date = fields.Date(string="Date")
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    ref_iq = fields.Char(string="Ref Iq")
    ref_name = fields.Char(string="Ref Name")
    ref_number = fields.Char(string="Reference Number")
    offer_currency = fields.Many2one("res.currency", string="Offer Currency")
    price_list = fields.Many2one("product.pricelist", string="Offer Pricelist")

    def cancel_offer(self):
        if self.related_sale_order:
            is_select_all = 0
            if self.related_sale_order.total_of_exchange_products:
                exchange_value = self.related_sale_order.total_of_exchange_products
                if self.related_sale_order.select_all_lines:
                    is_select_all = 1
                    line_idss = []
                    for rec in self.related_sale_order.order_line:
                        if rec.is_exchange:
                            line_idss.append(rec.id)
                else:
                    line_ids = []
                    for rec in self.related_sale_order.order_line:
                        if rec.is_exchange:
                            line_ids.append(rec.id)
                self.related_sale_order.action_cancel()
                if exchange_value:
                    self.related_sale_order.total_of_exchange_products = exchange_value
                if is_select_all == 1:
                    self.related_sale_order.select_all_lines = True
                    self.related_sale_order.total_of_exchange_products = 0.0
                    for rec in self.related_sale_order.order_line:
                        if rec.id in line_idss:
                            rec.is_exchange = True
                        else:
                            pass
                else:
                    for rec in self.related_sale_order.order_line:
                        if rec.id in line_ids:
                            rec.is_exchange = True
                        else:
                            pass
            else:
                self.related_sale_order.action_cancel()

        if self.purchase_order_ids:
            self.purchase_order_ids.button_cancel()

        self.state = "cancelled"
        self.message_post(
            body="Offer was cancelled by %s" % self.env.user.name,
            message_type='notification',
            # subtype='mail.mt_comment',
            partner_ids=[self.create_uid.partner_id.id])

    def approve_offer(self):
        if not self.ref_number:
            raise UserError(_('Reference number is required'))
        elif not self.offer_currency:
            raise UserError(_('Offer currency is required'))
        elif not self.price_list:
            raise UserError(_('Offer Price list is required'))
        else:
            self.managerial_approval = True
            self.state = "approved"
            self.message_post(
                body="Offer was approved  by %s" % self.env.user.name,
                message_type='notification',
                # subtype='mail.mt_comment',
                partner_ids=[self.create_uid.partner_id.id])

    def create_contract(self):
        if self.confirm_contract_data():
            ensure_none = self.env["contract.contract"].search(
                [("related_offering_record", "=", self.id)])
            if ensure_none:
                raise UserError(
                    _("Sorry, you cannot create a contract as a contract"
                      " already exists with this record as a parent"))
            else:
                list_of_line_contents = []
                for item in self.product_lines:
                    if item.qty == 1:
                        list_of_line_contents.append(
                            (0, 0, {
                                "product_id": item.product_id.id,
                                "product_char": item.product_id.name,
                                "price": item.offer_unit_price,
                                "qty": item.qty,
                                "config": item.config.id
                            }))
                    else:
                        for i in range(0, item.qty):
                            list_of_line_contents.append(
                                (0, 0, {
                                    "product_id": item.product_id.id,
                                    "product_char": item.product_id.name,
                                    "price": item.offer_unit_price,
                                    "qty": 1,
                                    "config": item.config.id
                                }))

                contract_vals = {
                    "partner_id": self.customer.id,
                    "related_offering_record": self.id,
                    "iq": self.iq,
                    "number": self.contract_no,
                    "signed_date": self.sign_date,
                    "contract_categ": self.contract_type,
                    "contract_signed_by": self.signed_by.id,
                    "product_lines": list_of_line_contents,
                }
                contract_id = self.env["contract.contract"].create(
                    contract_vals)
                if contract_id:
                    self.contract_created = True
                    self.related_contract = contract_id
                else:
                    raise UserError(
                        _("Contract Was Not Created For Some Reason"))
        else:
            raise UserError(
                _("One or more mandatory Contract fields has no value"))

    def create_purchase_order(self):
        print("hiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
        if not self.product_lines:
            raise UserError(_("product lines are empty"))

        # dictionary data: {vendor_id: vendor_currency }
        vendors = {}
        for offering_line in self.product_lines:
            # fetching the currency record because the saved one within the
            # config is not from res.currency
            res_currency_id = self.env['res.currency'].search(
                [('name', '=', offering_line.currency.currency_name)])
            for config_line in offering_line.config.product_bom_lines:
                # if vendor is not in dict
                if not vendors.get(config_line.vendor.id):
                    vendors[config_line.vendor.id] = res_currency_id.id
                #  if vendor is in dict but currency is different
                elif vendors.get(config_line.vendor.id) and vendors.get(
                        config_line.vendor.id) != res_currency_id.id:
                    raise UserError(
                        "Detected two currencies for the same vendor")

                #  if vendor is in dict and currency is the same
                else:
                    pass
        for vendor_id, currency_id in vendors.items():
            purchase_order_vals = {
                "partner_id": vendor_id,
                "origin": self.name,
                "currency_id": currency_id if currency_id else offering_line.config_currency.id,
                "related_offering_record": self.id,
                "date_planned": datetime.datetime.now()
            }
            list_of_line_contents = []
            for line in self.product_lines:
                qtyy = line.qty
                if line.discount:
                    discount = line.discount / 100
                else:
                    discount = 1
                for configline in line.config.product_bom_lines:
                    if configline.vendor.id == vendor_id:
                        list_of_line_contents.append((0, 0, {
                            "product_id": configline.product_id.id,
                            "price_unit": configline.total_price,
                            "product_qty": configline.qty * qtyy,
                            "name": configline.product_id.name,
                           }))
            purchase_order_vals["order_line"] = list_of_line_contents
            purchase_order_id = self.env["purchase.order"].create(
                purchase_order_vals)
            self.purchase_order_ids += purchase_order_id
        self.purchase_order_created = True

    def create_sale_order(self):
        if not self.customer:
            raise UserError(
                _("Please set a customer before creating a sale order"))
        if not self.product_lines:
            raise UserError(_("product lines are empty"))
        ensure_none = self.env["sale.order"].search(
            [("related_offering_record", "=", self.id)])
        if ensure_none:
            raise UserError(
                _("Sorry, You cant create a new sale order because a sale order already exists with this records as a parent,please delete it first"))
        sale_order_vals = {
            "partner_id": self.customer.id,
            "related_offering_record": self.id,
            "state": "draft",
            "pricelist_id": self.price_list.id,
            "project_num": self.iq
        }

        list_of_line_contents = []
        for item in self.product_lines:
            if item.discount:
                discount = item.discount * 100
                list_of_line_contents.append((0, 0, {
                    "product_id": item.product_id.id,
                    "config": item.config.id,
                    "price_unit": item.final_unit_price_usd if self.offer_currency.name == "USD" or self.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                    "product_uom_qty": item.qty,
                    "currency_id": self.offer_currency.id,
                    "discount": discount,
                }))
            else:
                list_of_line_contents.append((0, 0, {
                    "product_id": item.product_id.id,
                    "config": item.config.id,
                    "price_unit": item.final_unit_price_usd if self.offer_currency.name == "USD" or self.offer_currency.name == "EUR" else item.final_unit_price_iqd,
                    "product_uom_qty": item.qty,
                    "currency_id": self.offer_currency.id,
                }))
        sale_order_vals["order_line"] = list_of_line_contents
        sale_order_id = self.env["sale.order"].create(sale_order_vals)

        if sale_order_id:
            self.sale_order_created = True
            self.related_sale_order = sale_order_id
        else:
            raise UserError(_("Sale Order Was Not Created For Some Reason"))


    def view_purchase_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Offering Purchase Order',
            'view_type': 'form',
            'view_mode': 'list',
            'res_model': 'purchase.order',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('related_offering_record', '=', self.id)],
            'target': 'current',
            'context': {'default_related_offering_record': self.id}
        }
