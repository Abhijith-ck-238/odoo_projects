from odoo import fields, models


class LetterType(models.Model):
    _name = 'letter.type'
    _description = "Letter Type"

    name = fields.Char(string='Letter Type')