from odoo import fields, models


class LowerKsWorkSector(models.Model):
    _name = 'lower.ks.work.sector'
    _description = "Lower KS Work Sector"

    name = fields.Char(string='Work Sector')
