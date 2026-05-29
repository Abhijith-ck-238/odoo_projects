from odoo import fields, models


class LowerKsSpeciality(models.Model):
    _name = 'lower.ks.speciality'
    _description = "Lower KS Speciality"

    name = fields.Char(string='Speciality')
    color = fields.Integer("Color")