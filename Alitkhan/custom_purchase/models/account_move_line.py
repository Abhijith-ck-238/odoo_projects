from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    shipment_id = fields.Many2one('logistics.shipment', string="Shipment")