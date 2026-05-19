from odoo import models, fields, _


class RemoveDuplicateInventoryValuationEntries(models.Model):
    _name = "remove.duplicate.inventory.valuation"
    _description = 'Remove duplicate inventory valuation'

    def open_duplicated_inventory_valuation_entries(self):
        stock_valuation_layer_ids = self.env['stock.valuation.layer'].search(
            [('stock_move_id.location_id.usage', '=', 'supplier'), ('quantity', '>=', 0)])
        li = []
        for rec in stock_valuation_layer_ids:
            stock_valuation_layer = self.env['stock.valuation.layer'].search(
                [('stock_move_id', '=', rec.stock_move_id.id),
                 ('stock_move_id.location_id.usage', '=', 'supplier'), ('quantity', '>=', 0)
                 ])
            if len(stock_valuation_layer.ids) > 1:
                li = li + stock_valuation_layer.ids
        return {
            'name': _('Remove duplicate inventory valuation'),
            'view_mode': 'list',
            'res_model': 'stock.valuation.layer',
            'view_id': self.env.ref("custom_stock.stock_valuation_layer_tree_for_wizard").id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('id', 'in', li)],
        }
