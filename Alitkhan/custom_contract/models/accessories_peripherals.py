from odoo import models, fields


class Peripherals(models.Model):
    _name = 'peripheral.peripheral'
    _description = 'Peripherals and Accessories'

    name = fields.Char(string="Peripheral")
    part_number = fields.Char(string="Part Number")
    serial_no = fields.Char(string="Serial Number")
