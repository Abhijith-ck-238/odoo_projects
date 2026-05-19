# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseShippingType(models.Model):
    _name="purchase.shipping.type"

    name = fields.Char(string="Name")
