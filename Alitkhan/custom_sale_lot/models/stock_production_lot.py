from odoo import models, fields, api
from datetime import date
import datetime
from dateutil.relativedelta import relativedelta


class ProductionLot(models.Model):
    _inherit = 'stock.lot'

    product_unreserved_qty = fields.Float('Quantity', compute='_compute_product_unreserved_qty', store=True)
    date_alert_date = fields.Date('Alert Date', compute='_compute_date_alert_date')
    date_month = fields.Datetime(compute='_compute_date_month')

    @api.depends('use_date')
    def _compute_date_month(self):
        for lot in self:
            lot.date_month = False
            if lot.use_date:
                lot.date_month = date.today() + relativedelta(months=1)

    @api.depends('alert_date')
    def _compute_date_alert_date(self):
        for lot in self:
            lot.date_alert_date = False
            if lot.alert_date:
                lot.date_alert_date = lot.alert_date.date()

    def name_get(self):
        result = []
        for lot in self:
            name = lot.name + ', ' + str(lot.product_unreserved_qty)
            if lot.life_date:
                name = name + ', ' + str(lot.life_date.date())
            result.append((lot.id, name))
        return result

    @api.depends('quant_ids', 'quant_ids.reserved_quantity', 'product_qty')
    def _compute_product_unreserved_qty(self):
        for lot in self:
            # We only care for the quants in internal or transit locations.
            quants = lot.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
            lot.product_unreserved_qty = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))
