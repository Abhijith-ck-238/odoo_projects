from odoo import fields, models


class LcType(models.Model):
    _name = "lc.type"
    _inherit = ['mail.thread']
    _description = "L/C Type"

    name = fields.Char(string='L/C Type')
