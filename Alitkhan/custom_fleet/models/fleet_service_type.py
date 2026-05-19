from odoo import fields, models


class FleetServiceType(models.Model):
    _inherit = "fleet.service.type"

    notify_before_km = fields.Integer(string="Notify Before KM")
