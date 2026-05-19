from odoo import fields, models


class TicketType(models.Model):
    _name = 'ticket.type'
    _description = "Ticket Type"

    name = fields.Char(string='Ticket Type')