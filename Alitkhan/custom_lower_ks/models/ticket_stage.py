from odoo import fields, models

class LowerKsTicketStages(models.Model):
    _name = 'lower.ks.ticket.stage'
    _description = 'Lower Ks Ticket Stages'
    _order = 'sequence'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer()
