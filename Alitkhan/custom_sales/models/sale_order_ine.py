from odoo import models, fields, _, api

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    config = fields.Many2one('offering.config', string="Config")
    is_exchange = fields.Boolean(string="Is Exchange", default=False,
                                 copy=False)
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    vendor_price = fields.Float("Vendor Price")
