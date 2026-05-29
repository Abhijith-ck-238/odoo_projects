from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    modality_stage = fields.Boolean(string="Modality Stage")
    limited_users = fields.Many2many("res.users", string="Limited Users")
    ticket_must_be_invalid = fields.Boolean(string="Ticket Must Be Outside of Contract")
    auto_create_service_report = fields.Boolean(string="Auto Create Service Report")
    helpdesk_stage_id = fields.Many2one("helpdesk.stage", help="for field service tickets")
    require_service_report = fields.Boolean(string="Require Service Report", help="A ticket can not enter this stage without having a service report uploaded")