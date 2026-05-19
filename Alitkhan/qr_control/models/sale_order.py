# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    virtual_reservation_id = fields.Many2one('reserved.product', string="Virtual Reservation")
