# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class ItkanSale(models.Model): #this is implemented because they wanted the sale order date to be editable
    _inherit="sale.order"

    # date_order = fields.Datetime(string="Order Date", default=fields.Datetime.now)
    company_report_id = fields.Many2one('res.company', string="Company Report", default=lambda self: self.env.company)

    def action_confirm(self):
        for line in self.order_line:
            if line.product_id.categ_id.id == 1:
                raise UserError(_(f"Please set a category for product {line.product_id.display_name} before confirming this sale order"))
        res = super(ItkanSale, self).action_confirm()
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_smn = fields.Char(string="SMN")
        
    # For Importing Product By SMN
    @api.model
    def create(self, values):
        if values.get("product_smn"):
            smn = values["product_smn"]
            product_id = self.env['product.product'].search([('default_code', 'like', smn)])
            if len(product_id) > 1:
                raise UserError(_(f"More Than One Product Of The SMN {smn} Was Found. Please Contact Support"))
            elif len(product_id) == 1:
                values['product_id'] = product_id.id
            else:
                raise UserError(_(f"A Product with SMN {smn} was not  found"))

        result = super(SaleOrderLine, self).create(values)
        
        return result