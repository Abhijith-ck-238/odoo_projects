from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    lot_id = fields.Many2one('stock.lot', string="Lot/Serial Number", copy=False)

    @api.model_create_multi
    def create(self, vals):
        for value in vals:
            if value.get('sale_line_id'):
                sale_line_id = self.env['sale.order.line'].browse(value['sale_line_id'])
                if sale_line_id and sale_line_id.lot_id:
                    value.update({'lot_id': sale_line_id.lot_id.id})
        return super(StockMove, self).create(vals)

    def write(self,vals):
        res = super(StockMove, self).write(vals)
        for rec in self:
            if rec.sale_line_id and rec.picking_id and rec.lot_id and rec.move_line_ids and sum(rec.move_line_ids.mapped('qty_done')) == 0.0:
                for line in rec.move_line_ids:
                    line.lot_id = rec.lot_id.id
        return res
