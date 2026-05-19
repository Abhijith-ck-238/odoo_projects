from odoo import models, fields


class CompanyCompany(models.Model):
    _name = 'company.company'

    name = fields.Char(string="Company")
