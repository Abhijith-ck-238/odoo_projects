from odoo import fields, models


class GeneralLetterType(models.Model):
    _name = 'general.letter.type'
    _description = "General Letter Type"

    name = fields.Char(string='Letter Type')
