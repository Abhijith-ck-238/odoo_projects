from odoo import fields, models


class LowerKsAccount(models.Model):
    _name = 'lower.ks.account'
    _description = "Lower KS Account"

    name = fields.Char(string='Account')
