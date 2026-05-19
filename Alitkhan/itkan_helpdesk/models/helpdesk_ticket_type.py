from odoo import models, fields


class HelpdeskTicketType(models.Model):
    _name = 'helpdesk.ticket.type'
    _description = 'Helpdesk Ticket Type'
    _order = 'sequence'

    name = fields.Char('Type', required=True, translate=True)
    sequence = fields.Integer(default=10)
    require_service_report = fields.Boolean(default=True)

