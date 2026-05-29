# -*- coding: utf-8 -*-

from odoo import models, fields

class PurchaseRequiredDocuments(models.Model):
    _name="purchase.required.documents"

    name = fields.Char(string="Name")
