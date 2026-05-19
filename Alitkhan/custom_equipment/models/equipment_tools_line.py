from odoo import fields, models


class EquipmentTooolsLine(models.Model):
    _name = 'equipment.tools.line'
    _description = "Equipment Tools Line"

    equipment_id = fields.Many2one('equipment.equipment', "Equipment")
    tool_id = fields.Many2one('equipment.tools', "Tool")
    quantity = fields.Float("Quantity")
