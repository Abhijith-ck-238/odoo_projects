from odoo import models, fields, api


class Interval(models.Model):
    _name = 'interval.interval'
    _description = "Interval"

    name = fields.Char(string="Interval", required=True)
    value = fields.Integer(string="Value", required=True)
