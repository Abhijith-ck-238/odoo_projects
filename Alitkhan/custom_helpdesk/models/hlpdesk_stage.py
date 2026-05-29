from odoo import models, fields


class CustomHelpdeskStages(models.Model):
    _inherit = 'helpdesk.stage'

    is_restrict_ticket_move = fields.Boolean(string="Restrict ticket move")
    cancel_activities = fields.Boolean(string="Cancel Activities")
    is_field_service_ticket_exist = fields.Boolean(string="Is Field Service ticket Exist")
    send_notification_to_spare_parts_responsible = fields.Boolean(
        string="Send Notification to Spare Parts Responsible")
    archive_ticket = fields.Boolean(string="Archive Related Field Service")
    is_close = fields.Boolean("Closing stage")
