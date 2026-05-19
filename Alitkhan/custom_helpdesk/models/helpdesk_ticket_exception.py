from odoo import models, fields


class CustomHelpdeskTicketException(models.Model):
    _inherit = "helpdesk.ticket.exception"

    bypass_helpdesk_approval = fields.Boolean(string="Bypass Helpdesk Approval")
    bypass_field_service_approval = fields.Boolean(
        string="Bypass Field Service Approval")
    limit_helpdesk_approval = fields.Boolean(string="Limit Helpdesk Approval")
    limit_field_service_approval = fields.Boolean(
        string="Limit Field Service Approval")
