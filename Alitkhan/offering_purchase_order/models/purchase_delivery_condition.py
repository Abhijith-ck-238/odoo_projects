# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseDeliveryCondition(models.Model):
    """ they have more than Delivery condition,
        shipping type and required documents """
    _name="purchase.delivery.condition"

    name = fields.Char(string="Name")
