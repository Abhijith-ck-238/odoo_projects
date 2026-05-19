from odoo import fields, models

class ProjectStages(models.Model):
    _name = 'project.stage'
    _description = 'Project Stages'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()