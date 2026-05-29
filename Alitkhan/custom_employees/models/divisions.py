from odoo import models, fields


class Divisions(models.Model):
    _name = 'division.division'
    _description = 'Divisions'

    name = fields.Char(string="Divisions")


