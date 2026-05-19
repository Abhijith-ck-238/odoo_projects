from odoo import fields, models


class LowerKsProvince(models.Model):
    _name = 'lower.ks.province'
    _description = "Lower KS Province"

    name = fields.Char(string='Province')
