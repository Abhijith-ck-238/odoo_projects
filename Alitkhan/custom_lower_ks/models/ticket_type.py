from odoo import fields, models


class LowerKsTicketType(models.Model):
    _name = 'lower.ks.ticket.type'
    _description = "Lower KS Ticket Type"

    name = fields.Char(string='Ticket Type')
