# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SalesOrderLineExtItkModeA(models.Model):
    _inherit="sale.order.line"

    expiration_date = fields.Datetime(related="lot_id.expiration_date",string="Expiration Date",readonly=True)
    lot_notes = fields.Html(related="lot_id.note",string="Lot Notes",readonly=True)