from odoo import models, fields


class ShipmentType(models.Model):
    _name = "shipment.type"
    _description = "Shipment Type"


    name = fields.Char(string="Shipment Type")
