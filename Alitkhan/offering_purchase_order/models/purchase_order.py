# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseOrderExt(models.Model):
    _inherit="purchase.order"

    """ These fields are added to Purchase Model
             as per their request"""


    contract_id = fields.Many2one('contract.contract',string="Contract number")
    project_no = fields.Char(string="Project Number")
    delivery_time_Date =fields.Char(string="Delivery Time/Date")
    partial_shipment = fields.Char(string="Partial Shipment")
    transshipment = fields.Char(string="Transshipment")
    shipment_by = fields.Char(string="Shipment By")
    consignee_name = fields.Char(string="Consignee Name")
    payment_term = fields.Html(string="Payment Term")
    dispatch_address = fields.Html(string="Dispatch Address")
    end_user_address = fields.Html(string="End User Address")
    invoice_address = fields.Html(string="Invoice address")
    delivery_conditions = fields.Many2many(comodel_name="purchase.delivery.condition",relation="pur_del",column1="pur",column2="del",string="Delivery Conditions")
    type_of_shipping = fields.Many2many(comodel_name="purchase.shipping.type",relation="pur_ship",column1="pur",column2="ship",string="Type of Shipping")
    required_documents = fields.Many2many(comodel_name="purchase.required.documents",relation="pur_doc",column1="pur",column2="doc",string="Required Documents")
    product_specification = fields.Char(string="Product Specification")
    extra_notes = fields.Html(string="Notes")
    add_notes = fields.Boolean(string="Add notes in report ( keep False if notes are empty)") # this is added because I faced an issue in the Qweb template
