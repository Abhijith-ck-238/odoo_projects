from odoo import fields, models


class ProjectDepartment(models.Model):
    _name = "project.department"
    _description = "Project Department"

    name = fields.Char("Department Name")
    team_members = fields.Many2many('res.users', string="Department Members")
