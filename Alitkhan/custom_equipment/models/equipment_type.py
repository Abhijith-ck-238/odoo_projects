from odoo import fields, models


class EquipmentType(models.Model):
    _name = 'equipment.type'
    _description = 'Equipment Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Equipment Type')
