from odoo import fields, models


class SerialNumber(models.Model):
    _name = 'serial.number'
    _description = "Serial Number"

    name = fields.Char(string='Serial Number')
