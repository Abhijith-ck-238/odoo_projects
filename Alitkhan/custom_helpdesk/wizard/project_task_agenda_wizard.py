from odoo import models, fields


class ProjectTaskAgenda(models.TransientModel):
    _name = 'project.task.agenda'

    name = fields.Char(string="Task")
    task_id = fields.Many2one('project.task')
    agenda_id = fields.Many2one('agenda.agenda')
    user_id = fields.Many2one('res.users')
    date_start = fields.Datetime(string="Starting Date")
    date_end = fields.Datetime(string="Ending Date")
