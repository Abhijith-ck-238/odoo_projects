# Copyright 2014 Daniel Reis
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api,fields, models

_TASK_STATE = [
    ("draft", "New"),
    ("open", "In Progress"),
    ("pending", "Pending"),
    ("done", "Done"),
    ("cancelled", "Cancelled"),
]

class ProjectTask(models.Model):
    """Added state in the Project Task."""
    _inherit = "project.task"

    custom_state = fields.Selection(selection=_TASK_STATE ,related="stage_id.state", store=True)

