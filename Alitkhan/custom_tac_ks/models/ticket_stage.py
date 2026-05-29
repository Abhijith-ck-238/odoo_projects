from odoo import fields, models

class TicketStages(models.Model):
    _name = 'ticket.stage'
    _description = 'Ticket Stages'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()