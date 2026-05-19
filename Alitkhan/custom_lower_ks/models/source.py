from odoo import fields, models


class LowerKsSource(models.Model):
    _name = 'lower.ks.source'
    _description = "Lower KS Source"

    name = fields.Char(string='Source')