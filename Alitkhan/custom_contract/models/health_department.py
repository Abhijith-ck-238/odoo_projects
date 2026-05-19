from odoo import models, fields


class HealthDepartment(models.Model):
    _name = 'health.department'

    name = fields.Char(string="H.D Name")
