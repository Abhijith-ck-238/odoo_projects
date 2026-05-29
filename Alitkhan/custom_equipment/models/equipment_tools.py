from odoo import fields, models


class EquipmentTools(models.Model):
    _name = 'equipment.tools'
    _description = 'Equipment Tools'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Equipment Name")