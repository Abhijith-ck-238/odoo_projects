from odoo import fields, models


class ProjectType(models.Model):
    _name = 'project.type'
    _description = "Project Type"

    name = fields.Char(string='Ticket Type')
    checklist_ids = fields.One2many('project.checklist', 'project_type_id', string="Checklist")