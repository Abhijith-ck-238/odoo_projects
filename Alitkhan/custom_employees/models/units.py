from odoo import models, fields


class Units(models.Model):
    _name = 'unit.unit'
    _description = 'Units'

    name = fields.Char(string="Unit")


