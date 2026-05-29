
from odoo import models, fields, api, _
from odoo.exceptions import UserError



class ServiceReportsExt(models.Model):
    _inherit="service.report"


    task_id = fields.Many2one("project.task")