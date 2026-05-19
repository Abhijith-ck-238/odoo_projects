# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMoveExt(models.Model):
    _inherit = "stock.move.line"

    partner_id = fields.Many2one("res.partner",string="Customer",compute="compute_partner_id")
    life_date = fields.Datetime(string="Expiration",related="lot_id.expiration_date")
    # life_date = fields.Datetime(string="Expiration",related="lot_id.life_date")
    on_hand = fields.Float(string="Available in store QTY",related="product_id.qty_available")
    out_going = fields.Float(string="Out going",related="product_id.outgoing_qty")
    forcasted = fields.Float(string="On the way QTY",related="product_id.incoming_qty")



    def compute_partner_id(self):
        for rcd in self:
            if rcd.origin:
                if rcd.origin[0] == "S":
                    rcd.partner_id = self.env["sale.order"].search([("name","=",rcd.origin)]).partner_id.id 
                elif rcd.origin[0] == "P":
                    rcd.partner_id = self.env["purchase.order"].search([("name","=",rcd.origin)]).partner_id.id
                else:
                    rcd.partner_id = False
            else:
                rcd.partner_id = False


class ProductProductExt(models.Model):
    _inherit="product.product"

    LIST_OF_TYPES = [("Dx Non Siemens kit","Dx Non Siemens kit"),("spare part","spare part"),("equipment","equipment"),("Reagents","Reagents")]

    vendor = fields.Many2one("product.vendor",string="Vendor")
    product_type = fields.Selection(LIST_OF_TYPES,string="DX Product Type")

    


class ProductVendor(models.Model):
    _name = "product.vendor"
    _rec_name = "name"

    name = fields.Char(string="Vendor Name")