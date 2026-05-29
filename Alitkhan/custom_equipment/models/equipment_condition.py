from odoo import fields, models


class EquipmentCondition(models.Model):
    _name = 'equipment.condition'
    _description = 'Equipment Condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Equipment Condition")

