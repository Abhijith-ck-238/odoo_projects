from odoo import models, fields


class ShipmentTypeLines(models.Model):
    _name = 'shipment.type.lines'
    _description = "Shipment Type Line"

    partner_id = fields.Many2one('res.partner', string="Vendor")
    shipment_type_id = fields.Many2one('shipment.type', string="Shipment Type")
    total_value = fields.Float(string="Total Value")
    per_percentage = fields.Float(string="per %")
    shipment_id = fields.Many2one('logistics.shipment')

