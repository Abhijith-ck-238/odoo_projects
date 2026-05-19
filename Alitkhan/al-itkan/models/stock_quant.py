from odoo import models, fields, api

class StockQuant(models.Model):
    _inherit = "stock.quant"

    lot_expire_date = fields.Datetime(string="Lot Expiration Date", related="lot_id.expiration_date")