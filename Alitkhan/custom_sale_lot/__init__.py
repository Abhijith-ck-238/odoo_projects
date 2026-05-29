from . import models
from . import wizard


from odoo import api, SUPERUSER_ID


def set_stock_product_unreserved_qty(env):
    # env = api.Environment(cr, SUPERUSER_ID, {})

    lots = env['stock.lot'].search([])
    for lot in lots:
        quants = lot.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
        lot.product_unreserved_qty = sum(quants.mapped('quantity')) - sum(quants.mapped('reserved_quantity'))

