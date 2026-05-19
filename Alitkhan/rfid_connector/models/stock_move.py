from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    rfid_qty = fields.Float(string="RFID Qty")
