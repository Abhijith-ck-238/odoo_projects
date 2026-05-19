from odoo import models,fields


class ReservationReason(models.Model):
    _name = 'reservation.reason'

    name = fields.Char(string="Reservation Reason")
