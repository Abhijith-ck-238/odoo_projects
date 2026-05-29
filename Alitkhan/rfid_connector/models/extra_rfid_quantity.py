from odoo import fields, models


class ExtraRfidQuantity(models.Model):
    _name = 'extra.rfid.quantity'
    _description = "Extra RFID Quantity"

    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.lot', string='Lot')
    quantity = fields.Float('Quantity')
    picking_id = fields.Many2one('stock.picking')

