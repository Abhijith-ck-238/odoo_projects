from odoo import fields, models


class ProjectChecklist(models.Model):
    _name = "project.checklist"
    _description = "Project Checklist"

    name = fields.Char("Checklist Name")
    department_id =fields.Many2one('project.department', string="Department")
    days_for_project = fields.Integer(string="Days for Project")
    project_type_id = fields.Many2one('project.type')
    days_to_notify_before_deadline = fields.Integer(string="Days to Notify Before Deadline")
    is_subtask = fields.Boolean(string="Subtask")
