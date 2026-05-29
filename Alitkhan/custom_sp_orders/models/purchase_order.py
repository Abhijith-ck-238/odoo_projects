from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    sp_order_id = fields.Many2one('sp.order')

