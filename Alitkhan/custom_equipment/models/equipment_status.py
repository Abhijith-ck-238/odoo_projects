from odoo import fields, models


class EquipmentStatus(models.Model):
    _name = 'equipment.status'
    _description = 'Equipment Status'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Equipment Status")
