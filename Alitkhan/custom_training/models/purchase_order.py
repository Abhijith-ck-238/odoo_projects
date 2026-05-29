from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    training_id = fields.Many2one('training.ticket',string="Training")
