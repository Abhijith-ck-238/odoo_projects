from odoo import models, fields, api


class CustomStockPicking(models.Model):
    _inherit = 'stock.picking'

    x_studio_related_iq = fields.Char(related='sale_id.project_num')


class CustomStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    @api.model
    def unlink_selected_inventory_valuation_entries(self, selectedRecords):
        for rec in selectedRecords:
            stock_valuation_obj = self.env['stock.valuation.layer'].browse(rec)
            if stock_valuation_obj:
                stock_valuation_obj.unlink()
