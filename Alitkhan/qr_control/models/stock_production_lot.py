from odoo import api, fields, models
import datetime


class StockProductionLot(models.Model):
    _inherit = 'stock.lot'


    partner_ids = fields.Many2many('res.partner', string="Contact")
    product_available_qty = fields.Float(compute='_compute_product_available_qty', store=True)
    date = fields.Datetime(default= fields.datetime.now())
    date_after_30 = fields.Datetime(compute="compute_date_after_30")
    date_after_60 = fields.Datetime(compute="compute_date_after_60")
    product_category_id = fields.Many2one(related="product_id.categ_id", store=True)
    access_uint_id = fields.Many2one(related='product_id.unit_id', store=True)

    @api.depends('quant_ids', 'quant_ids.reserved_quantity', 'product_qty')
    def _compute_product_available_qty(self):
        for lot in self:
            # We only care for the quants in internal or transit locations.
            quants = lot.quant_ids.filtered(
                lambda q: q.location_id.usage in ['internal', 'transit'])
            lot.product_available_qty = sum(quants.mapped('quantity')) - sum(
                quants.mapped('reserved_quantity'))

    @api.depends('date', 'expiration_date')
    def compute_date_after_30(self):
        for rec in self:
            if rec.expiration_date:
                rec.date_after_30 = rec.date + datetime.timedelta(days=30)
            else:
                rec.date_after_30 =False

    @api.depends('date', 'expiration_date')
    def compute_date_after_60(self):
        for rec in self:
            if rec.expiration_date:
                rec.date_after_60 = rec.date + datetime.timedelta(days=60)
            else:
                rec.date_after_60 = False
