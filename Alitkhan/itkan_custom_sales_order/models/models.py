# -*- coding: utf-8 -*-

from odoo import models, fields, api
# CUSTOM REPORT TEMPLATE CREATED BY SHAMS@INTEGRATED PATH 


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    warranty=fields.Text(string="Warranty")
    project_num=fields.Char(string="Project Number")
    payment=fields.Html(string="Payment")
    import_licence= fields.Char(string="Import Licence")
    payment_by= fields.Char(string="Payment By")
    port_of_shipment= fields.Char(string="Port of Shipment")
    price_valid_for= fields.Char(string="Price Validation")
    delivery_period= fields.Char(string="Delivery Period")
    po_no = fields.Char(string="Purchase Order No.")
    job_no = fields.Char(string="Job Number")
    req = fields.Char(string="Requisitioner")
    date = fields.Char(string="DATED")
    supplier = fields.Char(string="Supplier")
    ship_to = fields.Char(string="Ship To")
    shipping_marks = fields.Char(string="Shipping Marks")
    total_amount_written = fields.Char(string="Total Amount In Writing")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def get_pack_line_price(self, pack_line):
        offering_id = self.order_id.related_offering_record
        offering_line = offering_id.product_lines.filtered(lambda x: x.product_id == self.product_id)
        config_id = offering_line.config
        config_line = config_id.product_bom_lines.filtered(lambda x: x.product_id == pack_line.product_id)
        # getting the price with the original currency
        line_price = config_line.price_unit * config_line.policy
        # converting the price if it was in a different currency
        if self.order_id.currency_id.name != config_id.currency.currency_name:
            line_price *= offering_line.exchange_rate_1

        if self.order_id.currency_id.name == 'IQD':
            line_price *= offering_line.exchange_rate

        return  round(line_price, 2)